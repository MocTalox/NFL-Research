from dataclasses import dataclass

from nfl.calcs import (
    BattlePokemon,
    BattleState,
    calc_damage,
    get_cpm,
    get_rcpm,
    get_tgr_cp,
    get_tgr_hp,
    get_tgr_stats,
)
from nfl.data import (
    PVP_MOVES,
    PokeSpecies,
)
from nfl.proto import (
    HoloCharacterCategory,
    HoloCombatType,
    HoloPokemonMove,
)


@dataclass
class DamageResult:
    stat: int
    damage: int


@dataclass
class DamageByLevel:
    level: float
    damage_by_stat: list[DamageResult]


@dataclass
class EnemyStats:
    attack: float
    defense: float
    hp: int
    cp: int


@dataclass
class CalculationResult:
    enemy_stats: EnemyStats
    damage_by_level: list[DamageByLevel]


def attack_breakpoints(
    pokemon_id: str,
    pokemon_form: str,
    pokemon_temp_evo: str,
    pokemon_alignment: str,
    pokemon_move: str,
    enemy_character: str,
    enemy_pokemon_id: str,
    enemy_pokemon_form: str,
    pokemon_min_atk: int,
    pokemon_max_atk: int,
    pokemon_min_level: int,
    pokemon_max_level: int,
    trainer_level: int,
) -> CalculationResult:
    pokemon_species = PokeSpecies.resolve(
        pokemon_id,
        pokemon_form,
        pokemon_temp_evo,
        pokemon_alignment,
    )
    enemy_species = PokeSpecies.resolve(
        enemy_pokemon_id,
        enemy_pokemon_form,
        alignment="Shadow",
    )

    enemy = HoloCharacterCategory[PokeSpecies.resolve_id(enemy_character)]
    move = HoloPokemonMove[PokeSpecies.resolve_id(pokemon_move)]

    a, d, _ = get_tgr_stats(enemy_species, trainer_level, enemy, 15, 15, 15)
    hp = get_tgr_hp(enemy_species, trainer_level, enemy, 15)
    cp = get_tgr_cp(enemy_species, trainer_level, enemy, 15, 15, 15)

    enemy_stats = EnemyStats(a, d, hp, cp)

    b = BattleState(HoloCombatType.VS_SEEKER)
    e = BattlePokemon(enemy_species, 15, 15, 15, get_rcpm(trainer_level), enemy)
    m = PVP_MOVES[move]

    damage_by_level: list[DamageByLevel] = []
    for level in range(pokemon_min_level * 2, pokemon_max_level * 2 + 1):
        level = level / 2
        damage_by_stat: list[DamageResult] = []
        for atk_iv in range(pokemon_min_atk, pokemon_max_atk + 1):
            p = BattlePokemon(pokemon_species, atk_iv, 15, 15, get_cpm(level))
            dmg = calc_damage(p, e, m, False, False, b)
            damage_by_stat.append(DamageResult(atk_iv, dmg))
        damage_by_level.append(DamageByLevel(level, damage_by_stat))

    return CalculationResult(enemy_stats, damage_by_level)


def defense_breakpoints(
    pokemon_id: str,
    pokemon_form: str,
    pokemon_temp_evo: str,
    pokemon_alignment: str,
    enemy_character: str,
    enemy_pokemon_id: str,
    enemy_pokemon_form: str,
    enemy_pokemon_move: str,
    pokemon_min_def: int,
    pokemon_max_def: int,
    pokemon_min_level: int,
    pokemon_max_level: int,
    trainer_level: int,
) -> CalculationResult:
    pokemon_species = PokeSpecies.resolve(
        pokemon_id,
        pokemon_form,
        pokemon_temp_evo,
        pokemon_alignment,
    )
    enemy_species = PokeSpecies.resolve(
        enemy_pokemon_id,
        enemy_pokemon_form,
        alignment="Shadow",
    )

    enemy = HoloCharacterCategory[PokeSpecies.resolve_id(enemy_character)]
    move = HoloPokemonMove[PokeSpecies.resolve_id(enemy_pokemon_move)]

    a, d, _ = get_tgr_stats(enemy_species, trainer_level, enemy, 15, 15, 15)
    hp = get_tgr_hp(enemy_species, trainer_level, enemy, 15)
    cp = get_tgr_cp(enemy_species, trainer_level, enemy, 15, 15, 15)

    enemy_stats = EnemyStats(a, d, hp, cp)

    b = BattleState(HoloCombatType.VS_SEEKER)
    e = BattlePokemon(enemy_species, 15, 15, 15, get_rcpm(trainer_level), enemy)
    m = PVP_MOVES[move]

    damage_by_level: list[DamageByLevel] = []
    for level in range(pokemon_min_level * 2, pokemon_max_level * 2 + 1):
        level = level / 2
        damage_by_stat: list[DamageResult] = []
        for def_iv in range(pokemon_min_def, pokemon_max_def + 1):
            p = BattlePokemon(pokemon_species, 15, def_iv, 15, get_cpm(level))
            dmg = calc_damage(e, p, m, False, False, b)
            damage_by_stat.append(DamageResult(def_iv, dmg))
        damage_by_level.append(DamageByLevel(level, damage_by_stat))

    return CalculationResult(enemy_stats, damage_by_level)
