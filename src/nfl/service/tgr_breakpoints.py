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
from nfl.exceptions import ValidationError
from nfl.proto import (
    HoloAlignment,
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
    pokemon: PokeSpecies,
    pokemon_move: HoloPokemonMove,
    enemy_character: HoloCharacterCategory,
    enemy_pokemon: PokeSpecies,
    pokemon_min_atk: int,
    pokemon_max_atk: int,
    pokemon_min_level: int,
    pokemon_max_level: int,
    trainer_level: int,
) -> CalculationResult:
    if enemy_pokemon.alignment is not HoloAlignment.SHADOW:
        raise ValidationError("SHADOW_ENEMY")

    a, d, _ = get_tgr_stats(poke=enemy_pokemon, level=trainer_level, enemy=enemy_character)
    hp = get_tgr_hp(poke=enemy_pokemon, level=trainer_level, enemy=enemy_character)
    cp = get_tgr_cp(poke=enemy_pokemon, level=trainer_level, enemy=enemy_character)

    enemy_stats = EnemyStats(a, d, hp, cp)

    state = BattleState(HoloCombatType.VS_SEEKER)
    enemy = BattlePokemon(
        enemy_pokemon, 15, 15, 15, get_rcpm(trainer_level), enemy_character
    )
    move = PVP_MOVES[pokemon_move]

    damage_by_level: list[DamageByLevel] = []
    for level in range(pokemon_min_level * 2, pokemon_max_level * 2 + 1):
        level = level / 2
        damage_by_stat: list[DamageResult] = []
        for atk_iv in range(pokemon_min_atk, pokemon_max_atk + 1):
            poke = BattlePokemon(pokemon, atk_iv, 15, 15, get_cpm(level))
            dmg = calc_damage(state, poke, enemy, move)
            damage_by_stat.append(DamageResult(atk_iv, dmg))
        damage_by_level.append(DamageByLevel(level, damage_by_stat))

    return CalculationResult(enemy_stats, damage_by_level)


def defense_breakpoints(
    pokemon: PokeSpecies,
    enemy_character: HoloCharacterCategory,
    enemy_pokemon: PokeSpecies,
    enemy_pokemon_move: HoloPokemonMove,
    pokemon_min_def: int,
    pokemon_max_def: int,
    pokemon_min_level: int,
    pokemon_max_level: int,
    trainer_level: int,
) -> CalculationResult:
    if enemy_pokemon.alignment is not HoloAlignment.SHADOW:
        raise ValidationError("SHADOW_ENEMY")

    a, d, _ = get_tgr_stats(poke=enemy_pokemon, level=trainer_level, enemy=enemy_character)
    hp = get_tgr_hp(poke=enemy_pokemon, level=trainer_level, enemy=enemy_character)
    cp = get_tgr_cp(poke=enemy_pokemon, level=trainer_level, enemy=enemy_character)

    enemy_stats = EnemyStats(a, d, hp, cp)

    state = BattleState(HoloCombatType.VS_SEEKER)
    enemy = BattlePokemon(
        enemy_pokemon, 15, 15, 15, get_rcpm(trainer_level), enemy_character
    )
    move = PVP_MOVES[enemy_pokemon_move]

    damage_by_level: list[DamageByLevel] = []
    for level in range(pokemon_min_level * 2, pokemon_max_level * 2 + 1):
        level = level / 2
        damage_by_stat: list[DamageResult] = []
        for def_iv in range(pokemon_min_def, pokemon_max_def + 1):
            poke = BattlePokemon(pokemon, 15, def_iv, 15, get_cpm(level))
            dmg = calc_damage(state, enemy, poke, move)
            damage_by_stat.append(DamageResult(def_iv, dmg))
        damage_by_level.append(DamageByLevel(level, damage_by_stat))

    return CalculationResult(enemy_stats, damage_by_level)
