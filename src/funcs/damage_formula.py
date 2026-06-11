from dataclasses import dataclass
from functools import reduce

from core.gm_holoholo import TYPES_ENUM
from core.gm_templates import BATTLE_SETTINGS, FRIENDSHIP_MILESTONE_SETTINGS, RAID_SETTINGS, TYPE_EFFECTIVE, WEATHER_AFFINITIES
from proto.msg.move_settings import MoveSettings
from proto.msg.pokemon_settings import PokemonSettings
from utils.utils import f32


remote_damage_modifier = RAID_SETTINGS.remote_damage_modifier
same_type_attack_bonus_multiplier = BATTLE_SETTINGS.same_type_attack_bonus_multiplier
dodge_damage_reduction_percent = BATTLE_SETTINGS.dodge_damage_reduction_percent
shadow_pokemon_attack_bonus_multiplier = BATTLE_SETTINGS.shadow_pokemon_attack_bonus_multiplier
shadow_pokemon_defense_bonus_multiplier = BATTLE_SETTINGS.shadow_pokemon_defense_bonus_multiplier
purified_pokemon_attack_multiplier_vs_shadow = BATTLE_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow

same_type_mega_boost = f32(1.3)
general_mega_boost = f32(1.1)
weather_attack_bonus_multiplier = f32(1.2)
blade_ae_attack_bonus_multiplier = f32(1.1)

types = {te.attack_type: te for te in TYPE_EFFECTIVE}
weather = {wa.weather_condition: wa for wa in WEATHER_AFFINITIES}
friend = [fms.attack_bonus_percentage for fms in sorted(
    [fms for fms in FRIENDSHIP_MILESTONE_SETTINGS],
    key=lambda fms: fms.min_points_to_reach + fms.relative_points_to_reach
)]

@dataclass
class Pokemon:
    pokemon_settings: PokemonSettings | None = None
    atk_iv: int = 0
    def_iv: int = 0
    sta_iv: int = 0
    cpm: float = 0.0
    shadow: bool = False
    purified: bool = False

@dataclass
class BattleState:
    mega_boosted_types: tuple[str] | None = None
    weather_id: str | None = None
    friendship_level: int = 0
    blade_ae: bool = False
    bash_ae: bool = False

def get_mega_boost(move_type: str, mega_boosted_types: tuple[str] | None) -> float:
    if not mega_boosted_types:
        return 1.0
    return same_type_mega_boost if move_type in mega_boosted_types else general_mega_boost

def get_purified_attack_bonus(purified_attacker: bool, shadow_target: bool) -> float:
    return purified_pokemon_attack_multiplier_vs_shadow if purified_attacker and shadow_target else 1.0

def get_shadow_attack_bonus(shadow_attacker: bool, shadow_target: bool) -> float:
    shadow_attack_bonus = shadow_pokemon_attack_bonus_multiplier if shadow_attacker else 1.0
    shadow_defense_bonus = shadow_pokemon_defense_bonus_multiplier if shadow_target else 1.0
    return f32(shadow_attack_bonus / shadow_defense_bonus)

def get_weather_boost(move_type: str, weather_id: str | None) -> float:
    if not weather_id:
        return 1.0
    return weather_attack_bonus_multiplier if move_type in weather[weather_id].pokemon_type else 1.0

def get_stab(move_type: str, atk_type_1: str, atk_type_2: str | None) -> float:
    return same_type_attack_bonus_multiplier if move_type == atk_type_1 or move_type == atk_type_2 else 1.0

def get_fiendship_boost(friend_level: int) -> float:
    return friend[friend_level] if friend_level >= 0 else 1.0

def get_effect(move_type: str, def_type_1: str, def_type_2: str | None = None) -> float:
    if def_type_2:
        return get_effect(move_type, def_type_1) * get_effect(move_type, def_type_2)
    return types[move_type].attack_scalar[TYPES_ENUM[def_type_1] - 1]

def get_dodge_boost(dodged: bool) -> float:
    return f32(1.0 - dodge_damage_reduction_percent) if dodged else 1.0

def get_blade_boost(blade: bool) -> float:
    return blade_ae_attack_bonus_multiplier if blade else 1.0

def damage_formula(
    attacker: Pokemon,
    target: Pokemon,
    move_settings: MoveSettings,
    state: BattleState,
) -> int:
    base_damage = damage_formula_raw(
        attacker,
        target,
        move_settings,
        state,
    )

    return int(f32(base_damage + 1.0))

def damage_formula_raw(
    attacker: Pokemon,
    target: Pokemon,
    move_settings: MoveSettings,
    state: BattleState,
) -> float:
    assert attacker.pokemon_settings and attacker.cpm
    assert target.pokemon_settings and target.cpm
    attack_term = f32(attacker.cpm * (attacker.atk_iv + attacker.pokemon_settings.stats.base_attack))
    defense_term = f32(target.cpm * (target.def_iv + target.pokemon_settings.stats.base_defense))
    attack_ratio = f32(f32(attack_term * move_settings.power) / defense_term)

    multipliers = [
        remote_damage_modifier,
        get_mega_boost(move_settings.pokemon_type, state.mega_boosted_types),
        get_purified_attack_bonus(attacker.purified, target.shadow),
        get_shadow_attack_bonus(attacker.shadow, target.shadow),
        get_weather_boost(move_settings.pokemon_type, state.weather_id),
        get_stab(move_settings.pokemon_type, attacker.pokemon_settings.type, attacker.pokemon_settings.type_2),
        get_fiendship_boost(state.friendship_level),
        get_effect(move_settings.pokemon_type, target.pokemon_settings.type, target.pokemon_settings.type_2),
        # Unknown modifiers
        get_dodge_boost(False),
        get_blade_boost(False),
        attack_ratio,
        0.5,
    ]

    return reduce(lambda a, b: f32(a * b), multipliers, 1.0)
