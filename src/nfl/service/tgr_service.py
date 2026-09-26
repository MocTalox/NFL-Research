import math
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import product

from nfl.calcs import (
    BattlePokemon,
    BattleState,
    DummyMove,
    DummyPokemon,
    calc_damage,
    get_cpm,
    get_rcpm,
)
from nfl.data import (
    POKEMON,
    PVP_MOVES,
    PokeData,
    PokeSpecies,
)
from nfl.data.catalog import get_pokemon_settings_temp_evo
from nfl.exceptions import NotFoundError
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
    type_1: HoloPokemonType
    type_2: HoloPokemonType
    attack: int
    defense: int
    stamina: int
    quick_moves: list[HoloPokemonMove]
    charged_moves: list[HoloPokemonMove]

    def is_the_same(self, other: PokeSpecies) -> bool:
        if not isinstance(other, _PokemonData):
            return False
        if self is other:
            return True
        return (
            self.name == other.name
            and self.temp_evo == other.temp_evo
            and self.alignment == other.alignment
            and self.type_1 == other.type_1
            and self.type_2 == other.type_2
            and self.attack == other.attack
            and self.defense == other.defense
            and self.stamina == other.stamina
            and self.quick_moves == other.quick_moves
            and self.charged_moves == other.charged_moves
        )


@dataclass(frozen=True)
class _EnemyData:
    type_1: HoloPokemonType
    type_2: HoloPokemonType
    defense: int
    alignment: HoloAlignment
    move_type: HoloPokemonType


@dataclass(frozen=True)
class _PokemonMoveSet:
    pokemon: _PokemonData
    quick: CombatMove
    charged: CombatMove


@dataclass(frozen=True)
class MoveSetRanking:
    pokemon: _PokemonMoveSet  # TODO visibility or structure fix
    damage_per_turn: float
    charged_damage: float
    charged_index: float
    charged_rate: float
    total_bulk: float


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
    charged_moves = [
        *pokemon_settings.cinematic_moves,
        *pokemon_settings.elite_cinematic_move,
        *pokemon_settings.non_tm_cinematic_moves,
        *pokemon_settings.legacy_cinematic_moves,
    ]

    if pokemon_settings.shadow is not None:
        if alignment == HoloAlignment.SHADOW:
            charged_moves.append(pokemon_settings.shadow.shadow_charge_move)
        if alignment == HoloAlignment.PURIFIED:
            charged_moves.append(pokemon_settings.shadow.purified_charge_move)

    if pokemon_settings.nfl_special_move:
        charged_moves.append(pokemon_settings.nfl_special_move)

    return _PokemonData(
        name=pokemon_settings.pokemon_id,
        form=pokemon_settings.form,
        temp_evo=temp_evo_id,
        alignment=alignment,
        type_1=pokemon_settings.type,
        type_2=pokemon_settings.type_2,
        attack=pokemon_settings.stats.base_attack,
        defense=pokemon_settings.stats.base_defense,
        stamina=pokemon_settings.stats.base_stamina,
        quick_moves=quick_moves,
        charged_moves=charged_moves,
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


_COMBAT_TYPE = HoloCombatType.VS_SEEKER


# =========================
# DATA GENERATION
# =========================


def _gen_pokemon_instances(
    poke: _PokemonData, include_charged: bool = False
) -> Iterator[_PokemonMoveSet]:
    poke_charged_moves = (
        poke.charged_moves if include_charged else poke.charged_moves[:1]
    )

    for quick, charged in product(poke.quick_moves, poke_charged_moves):
        yield _PokemonMoveSet(poke, PVP_MOVES[quick], PVP_MOVES[charged])


# =========================
# RANKING
# =========================


def tgr_best_pokemon_moveset(
    poke_species: PokeSpecies,
    enemy_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_type_2: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_defense: int = 150,
    rounded: bool = False,
) -> list[MoveSetRanking]:

    pokemon = _POKEMON_DATA.get(poke_species)
    if pokemon is None:
        raise NotFoundError("MISSIGN_SPECIES_DATA", poke_species=poke_species)

    defender = _EnemyData(
        enemy_type,
        enemy_type_2,
        enemy_defense,
        HoloAlignment.SHADOW,
        HoloPokemonType.POKEMON_TYPE_NONE,
    )

    rankings = [
        _create_ranking(p, defender, rounded)
        for p in _gen_pokemon_instances(pokemon, True)
    ]

    return sorted(
        rankings, key=lambda r: (r.damage_per_turn, r.charged_index), reverse=True
    )


def tgr_best_attackers(
    pokemon_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_type_2: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
    enemy_defense: int = 150,
    limit: int = 100,
    exclude_purified: bool = True,
    exclude_temp_evos: bool = True,
    rounded: bool = False,
) -> list[MoveSetRanking]:

    defender = _EnemyData(
        enemy_type,
        enemy_type_2,
        enemy_defense,
        HoloAlignment.SHADOW,
        enemy_type,  # TODO separate enemy move type
    )

    rankings: list[MoveSetRanking] = []

    for poke in _POKEMON_DATA.get_all_pokes():
        if exclude_purified and poke.alignment == HoloAlignment.PURIFIED:
            continue
        if exclude_temp_evos and poke.temp_evo:
            continue

        candidates = (
            p
            for p in _gen_pokemon_instances(poke)
            if not pokemon_type or p.quick.type == pokemon_type
        )
        best = max(
            candidates,
            key=lambda p: _tgr_calc_damage_per_turn(p, defender, rounded),
            default=None,
        )

        if best is not None:
            rankings.append(_create_ranking(best, defender, rounded))

    return sorted(rankings, key=lambda r: r.damage_per_turn, reverse=True)[:limit]


def _create_ranking(
    poke: _PokemonMoveSet, defender: _EnemyData, rounded: bool
) -> MoveSetRanking:

    return MoveSetRanking(
        pokemon=poke,
        damage_per_turn=_tgr_calc_damage_per_turn(poke, defender, rounded),
        charged_damage=_tgr_calc_charged_damage(poke, defender, rounded),
        charged_index=_tgr_calc_charged_index(poke, defender, rounded),
        charged_rate=_tgr_calc_charged_rate(poke.quick, poke.charged),
        total_bulk=_tgr_calc_total_bulk(poke.pokemon, defender),
    )



# =========================
# CALCULATIONS
# =========================


def _tgr_calc_damage(
    attacker: PokeSpecies, combat_move: CombatMove, defender: _EnemyData, rounded: bool
) -> float:
    enemy = DummyPokemon(
        0, defender.defense, 0, defender.type_1, defender.type_2, defender.alignment
    )

    return calc_damage(
        BattleState(HoloCombatType.VS_SEEKER),
        BattlePokemon(attacker, 15, 15, 15, get_cpm(50)),
        BattlePokemon(enemy, 15, 15, 15, get_rcpm(80)),
        combat_move,
        rounded=rounded,
    )


def _tgr_calc_damage_per_turn(
    attacker: _PokemonMoveSet, defender: _EnemyData, rounded: bool
) -> float:
    damage = _tgr_calc_damage(attacker.pokemon, attacker.quick, defender, rounded)

    return damage / (attacker.quick.duration_turns + 1)


def _tgr_calc_charged_damage(
    attacker: _PokemonMoveSet, defender: _EnemyData, rounded: bool
) -> float:
    return _tgr_calc_damage(attacker.pokemon, attacker.charged, defender, rounded)


def _tgr_calc_charged_index(
    attacker: _PokemonMoveSet, defender: _EnemyData, rounded: bool
) -> float:
    damage_per_turn = _tgr_calc_damage_per_turn(attacker, defender, rounded)
    charged_damage = _tgr_calc_charged_damage(attacker, defender, rounded)

    if damage_per_turn == 0:
        return math.inf

    return charged_damage / (21 * damage_per_turn)


def _tgr_calc_charged_rate(quick: CombatMove, charged: CombatMove) -> float:
    if quick.energy_delta == 0:
        return math.inf

    return -1 * charged.energy_delta / quick.energy_delta * (quick.duration_turns + 1)


def _tgr_calc_total_bulk(
    attacker: _PokemonData, defender: _EnemyData
) -> float:
    enemy = DummyPokemon(
        100, 0, 0, defender.type_1, defender.type_2, defender.alignment
    )
    combat_move = DummyMove(10, defender.move_type)

    damage = calc_damage(
        BattleState(HoloCombatType.VS_SEEKER),
        BattlePokemon(enemy, 15, 15, 15, get_rcpm(80)),
        BattlePokemon(attacker, 15, 15, 15, get_cpm(50)),
        combat_move,
        rounded=False,
    )

    return (attacker.defense + 15) * (attacker.stamina + 15) / damage
