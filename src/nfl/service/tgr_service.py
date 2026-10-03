import math
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import product

from nfl.calcs import calc_damage, get_cpm, get_hp, get_rcpm
from nfl.data import (
    POKEMON,
    PVP_MOVES,
    PokeData,
    PokeSpecies,
)
from nfl.data.catalog import get_pokemon_settings_temp_evo
from nfl.exceptions import NotFoundError
from nfl.models import (
    BattleDummyMove,
    BattleDummyPokemon,
    BattlePokemon,
    BattleState,
    TgrMovesetData,
    TgrPokemonMoveset,
)
from nfl.proto import (
    CombatMove,
    HoloAlignment,
    HoloCombatType,
    HoloPokemonMove,
    HoloPokemonType,
    HoloTempEvoId,
    PokemonSettings,
)


@dataclass(frozen=True)
class _PokemonData(PokeSpecies):
    quick_moves: list[HoloPokemonMove]
    charge_moves: list[HoloPokemonMove]
    special_move: HoloPokemonMove

    def is_the_same(self, other: PokeSpecies) -> bool:
        if not isinstance(other, _PokemonData):
            return False
        if self is other:
            return True
        return (
            self.name == other.name
            and self.temp_evo == other.temp_evo
            and self.alignment == other.alignment
            and self.quick_moves == other.quick_moves
            and self.charge_moves == other.charge_moves
            and self.special_move == other.special_move
        )


@dataclass(frozen=True)
class _EnemyData:
    battle_pokemon: BattlePokemon
    dummy_move: BattleDummyMove


@dataclass(frozen=True)
class _PokemonInstance:
    pokemon_species: PokeSpecies
    battle_pokemon: BattlePokemon
    quick: CombatMove
    charge: CombatMove
    temp_evo_level: int


def _to_pokemon_data(
    pokemon_settings: PokemonSettings,
    temp_evo_id: HoloTempEvoId = HoloTempEvoId.TEMP_EVOLUTION_UNSET,
    alignment: HoloAlignment = HoloAlignment.ALIGNMENT_UNSET,
):
    if temp_evo_id:
        pokemon_settings = get_pokemon_settings_temp_evo(pokemon_settings, temp_evo_id)

    quick_moves = [
        *pokemon_settings.quick_moves,
        *pokemon_settings.elite_quick_move,
        *pokemon_settings.legacy_quick_moves,
    ]
    charge_moves = [
        *pokemon_settings.cinematic_moves,
        *pokemon_settings.elite_cinematic_move,
        *pokemon_settings.non_tm_cinematic_moves,
        *pokemon_settings.legacy_cinematic_moves,
    ]

    if pokemon_settings.shadow is not None:
        if alignment == HoloAlignment.SHADOW:
            charge_moves.append(pokemon_settings.shadow.shadow_charge_move)
        if alignment == HoloAlignment.PURIFIED:
            charge_moves.append(pokemon_settings.shadow.purified_charge_move)

    return _PokemonData(
        name=pokemon_settings.pokemon_id,
        form=pokemon_settings.form,
        temp_evo=temp_evo_id,
        alignment=alignment,
        quick_moves=quick_moves,
        charge_moves=charge_moves,
        special_move=pokemon_settings.nfl_special_move,
    )


def _unfold_settings(pokemon_settings: PokemonSettings):
    res: list[_PokemonData] = []

    res.append(_to_pokemon_data(pokemon_settings))

    if pokemon_settings.shadow:
        res.append(_to_pokemon_data(pokemon_settings, alignment=HoloAlignment.SHADOW))
        res.append(_to_pokemon_data(pokemon_settings, alignment=HoloAlignment.PURIFIED))
    for temp_evo in pokemon_settings.temp_evo_overrides:
        res.append(_to_pokemon_data(pokemon_settings, temp_evo_id=temp_evo.temp_evo_id))
        if pokemon_settings.shadow:
            res.append(
                _to_pokemon_data(
                    pokemon_settings,
                    temp_evo_id=temp_evo.temp_evo_id,
                    alignment=HoloAlignment.PURIFIED,
                )
            )

    return res


_POKEMON_DATA: PokeData[_PokemonData] = PokeData(POKEMON, _unfold_settings)


def get_all_pokemon() -> list[PokeSpecies]:
    return sorted(_POKEMON_DATA.get_all_species())


# =========================
# DATA GENERATION
# =========================


def _gen_pokemon_instances(
    pokemon: _PokemonData,
    level: float,
    atk_iv: int,
    def_iv: int,
    include_charge: bool = False,
) -> Iterator[_PokemonInstance]:
    bp = BattlePokemon(pokemon, atk_iv, def_iv, 15, get_cpm(level))
    charge_moves = pokemon.charge_moves if include_charge else pokemon.charge_moves[:1]

    for quick, charge in product(pokemon.quick_moves, charge_moves):
        data_quick = PVP_MOVES[quick]
        data_charge = PVP_MOVES[charge]
        yield _PokemonInstance(pokemon, bp, data_quick, data_charge, 0)

    if include_charge and pokemon.special_move:
        data_charge = PVP_MOVES[pokemon.special_move]
        for quick in pokemon.quick_moves:
            data_quick = PVP_MOVES[quick]
            for mega_level in range(5):
                yield _PokemonInstance(pokemon, bp, data_quick, data_charge, mega_level)


# =========================
# RANKING
# =========================


def tgr_best_pokemon_moveset(
    poke_species: PokeSpecies,
    enemy_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_type_2: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    pokemon_level: float = 50.0,
    pokemon_atk_iv: int = 15,
    enemy_level: int = 80,
    enemy_defense: int = 150,
    rounded: bool = False,
) -> list[TgrMovesetData]:

    pokemon = _POKEMON_DATA.get(poke_species)
    if pokemon is None:
        raise NotFoundError("MISSIGN_SPECIES_DATA", poke_species=poke_species)

    enemy_data = BattleDummyPokemon(
        base_def=enemy_defense,
        type_1=enemy_type,
        type_2=enemy_type_2,
        alignment=HoloAlignment.SHADOW,
    )
    enemy = _EnemyData(
        BattlePokemon(enemy_data, 15, 15, 15, get_rcpm(enemy_level)),
        BattleDummyMove(0, HoloPokemonType.POKEMON_TYPE_NONE),
    )

    rankings = [
        _create_ranking(p, enemy, rounded)
        for p in _gen_pokemon_instances(
            pokemon, pokemon_level, pokemon_atk_iv, 15, True
        )
    ]

    return sorted(
        rankings, key=lambda r: (r.damage_per_turn, r.charge_index), reverse=True
    )


def tgr_best_attackers(
    pokemon_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_type_2: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    pokemon_level: float = 50.0,
    pokemon_atk_iv: int = 15,
    pokemon_def_iv: int = 15,
    enemy_level: int = 80,
    enemy_attack: int = 150,
    enemy_defense: int = 150,
    enemy_move_power: float = 10.0,
    enemy_move_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    limit: int = 50,
    only_best_moveset: bool = True,
    exclude_purified: bool = True,
    exclude_temp_evos: bool = True,
    rounded: bool = False,
) -> list[TgrMovesetData]:

    enemy_data = BattleDummyPokemon(
        base_atk=enemy_attack,
        base_def=enemy_defense,
        type_1=enemy_type,
        type_2=enemy_type_2,
        alignment=HoloAlignment.SHADOW,
    )
    enemy = _EnemyData(
        BattlePokemon(enemy_data, 15, 15, 15, get_rcpm(enemy_level)),
        BattleDummyMove(enemy_move_power, enemy_move_type),
    )

    rankings: list[TgrMovesetData] = []

    for poke in _POKEMON_DATA.get_all_pokes():
        if exclude_purified and poke.alignment == HoloAlignment.PURIFIED:
            continue
        if exclude_temp_evos and poke.temp_evo:
            continue

        candidates = filter(
            lambda p: not pokemon_type or p.quick.type == pokemon_type,
            _gen_pokemon_instances(poke, pokemon_level, pokemon_atk_iv, pokemon_def_iv),
        )
        if only_best_moveset:
            best = max(
                candidates,
                key=lambda p: _tgr_calc_damage_per_turn(p, enemy, rounded),
                default=None,
            )
            candidates = (best,) if best is not None else ()

        for candidate in candidates:
            rankings.append(_create_ranking(candidate, enemy, rounded))

    return sorted(rankings, key=lambda r: r.damage_per_turn, reverse=True)[:limit]


def _create_ranking(
    poke: _PokemonInstance, enemy: _EnemyData, rounded: bool
) -> TgrMovesetData:

    return TgrMovesetData(
        moveset=TgrPokemonMoveset(
            pokemon=poke.pokemon_species,
            quick=poke.quick.unique_id,
            charge=poke.charge.unique_id,
        ),
        damage_per_turn=_tgr_calc_damage_per_turn(poke, enemy, rounded),
        charge_damage=_tgr_calc_charge_damage(poke, enemy, rounded),
        charge_index=_tgr_calc_charge_index(poke, enemy, rounded),
        charge_rate=_tgr_calc_charge_rate(poke.quick, poke.charge),
        total_bulk=_tgr_calc_total_bulk(poke, enemy, rounded),
    )


# =========================
# CALCULATIONS
# =========================


def _tgr_calc_damage_per_turn(
    pokemon: _PokemonInstance, enemy: _EnemyData, rounded: bool
) -> float:
    damage = calc_damage(
        BattleState(HoloCombatType.VS_SEEKER),
        pokemon.battle_pokemon,
        enemy.battle_pokemon,
        pokemon.quick,
        rounded=rounded,
    )

    return damage / (pokemon.quick.duration_turns + 1)


def _tgr_calc_charge_damage(
    pokemon: _PokemonInstance, enemy: _EnemyData, rounded: bool
) -> float:
    return calc_damage(
        BattleState(HoloCombatType.VS_SEEKER, pokemon.temp_evo_level),
        pokemon.battle_pokemon,
        enemy.battle_pokemon,
        pokemon.charge,
        rounded=rounded,
    )


def _tgr_calc_charge_index(
    pokemon: _PokemonInstance, enemy: _EnemyData, rounded: bool
) -> float:
    damage_per_turn = _tgr_calc_damage_per_turn(pokemon, enemy, rounded)
    charge_damage = _tgr_calc_charge_damage(pokemon, enemy, rounded)

    if damage_per_turn == 0:
        return math.inf

    return charge_damage / (21 * damage_per_turn)


def _tgr_calc_charge_rate(quick: CombatMove, charge: CombatMove) -> float:
    if quick.energy_delta == 0:
        return math.inf

    return -1 * charge.energy_delta / quick.energy_delta * (quick.duration_turns + 1)


def _tgr_calc_total_bulk(
    pokemon: _PokemonInstance, enemy: _EnemyData, rounded: bool
) -> float:
    damage = calc_damage(
        BattleState(HoloCombatType.VS_SEEKER),
        enemy.battle_pokemon,
        pokemon.battle_pokemon,
        enemy.dummy_move,
        rounded=rounded,
    )

    hp = get_hp(
        poke=pokemon.pokemon_species,
        cpm=pokemon.battle_pokemon.cpm,
        iv_sta=pokemon.battle_pokemon.sta_iv,
    )

    return hp / damage
