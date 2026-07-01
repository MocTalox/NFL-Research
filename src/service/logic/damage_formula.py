from dataclasses import dataclass
from functools import reduce

from core.gm_holoholo import HoloPokemonType, HoloWeatherCondition, HoloCharacterCategory, HoloCombatType, HoloFriendshipLevel
from core.gm_templates import BATTLE_SETTINGS, RAID_SETTINGS, COMBAT_SETTINGS, WEATHER_BONUS_SETTINGS, MEGA_EVO_SETTINGS
from proto.msg.combat_move import CombatMove
from proto.msg.move_settings import MoveSettings
from proto.msg.pokemon_settings import PokemonSettings
from service.common.data import WEATHER, TYPES, FRIENDSHIP_DMG_BONUS, BEHEMOTH_BLADE_AE, BEHEMOTH_BASH_AE
from service.logic.pokemon_stats import get_stats, get_tgr_stats
from utils.float32 import f32


@dataclass
class Pokemon:
    pokemon_settings: PokemonSettings | None = None
    atk_iv: int = 0
    def_iv: int = 0
    sta_iv: int = 0
    cpm: float = 0.0
    shadow: bool = False
    purified: bool = False
    tgr_member: HoloCharacterCategory = HoloCharacterCategory(0)

@dataclass
class BattleState:
    combat_type: HoloCombatType
    mega_boosted_types: tuple[HoloPokemonType] | None = None
    weather_id: HoloWeatherCondition = HoloWeatherCondition(0)
    friendship_level: HoloFriendshipLevel = HoloFriendshipLevel(0)
    remote_raid: bool = False
    blade_ae: bool = False
    bash_ae: bool = False

@dataclass(frozen=True)
class DamageMultipliers:
    fast_attack: float = 1.0
    charge_attack: float = 1.0
    same_type_attack: float = 1.0
    dodge_damage_reduction: float = 1.0
    weather_attack: float = 1.0
    friendship_attack: dict[HoloFriendshipLevel, float] = {}
    shadow_pokemon_attack: float = 1.0
    shadow_pokemon_defense: float = 1.0
    purified_pokemon_attack: float = 1.0 # vs shadow only (unused in-game)
    same_type_mega_attack: float = 1.0
    different_type_mega_attack: float = 1.0
    remote_attack: float = 1.0
    blade_ae_attack: float = 1.0
    bash_ae_defense: float = 1.0

_DAMAGE_MULTIPLIERS = {
    HoloCombatType.VS_SEEKER: DamageMultipliers(
        fast_attack=COMBAT_SETTINGS.fast_attack_bonus_multiplier,
        charge_attack=COMBAT_SETTINGS.charge_attack_bonus_multiplier,
        same_type_attack=COMBAT_SETTINGS.same_type_attack_bonus_multiplier,
        shadow_pokemon_attack=COMBAT_SETTINGS.shadow_pokemon_attack_bonus_multiplier,
        shadow_pokemon_defense=COMBAT_SETTINGS.shadow_pokemon_defense_bonus_multiplier,
        purified_pokemon_attack=COMBAT_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow,
    ),
    HoloCombatType.SOLO: DamageMultipliers(
        same_type_attack=BATTLE_SETTINGS.same_type_attack_bonus_multiplier,
        dodge_damage_reduction=BATTLE_SETTINGS.dodge_damage_reduction_percent,
        weather_attack=WEATHER_BONUS_SETTINGS.attack_bonus_multiplier,
        friendship_attack=FRIENDSHIP_DMG_BONUS,
        shadow_pokemon_attack=BATTLE_SETTINGS.shadow_pokemon_attack_bonus_multiplier,
        shadow_pokemon_defense=BATTLE_SETTINGS.shadow_pokemon_defense_bonus_multiplier,
        purified_pokemon_attack=BATTLE_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow,
        same_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_same_type,
        different_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_different_type,
    ),
    HoloCombatType.COMBAT_TYPE_RAID: DamageMultipliers(
        same_type_attack=BATTLE_SETTINGS.same_type_attack_bonus_multiplier,
        dodge_damage_reduction=BATTLE_SETTINGS.dodge_damage_reduction_percent,
        weather_attack=WEATHER_BONUS_SETTINGS.attack_bonus_multiplier,
        friendship_attack=FRIENDSHIP_DMG_BONUS,
        shadow_pokemon_attack=BATTLE_SETTINGS.shadow_pokemon_attack_bonus_multiplier,
        shadow_pokemon_defense=BATTLE_SETTINGS.shadow_pokemon_defense_bonus_multiplier,
        purified_pokemon_attack=BATTLE_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow,
        remote_attack=RAID_SETTINGS.remote_damage_modifier,
        same_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_same_type,
        different_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_different_type,
        blade_ae_attack=BEHEMOTH_BLADE_AE[HoloCombatType.COMBAT_TYPE_RAID],
        bash_ae_defense=BEHEMOTH_BASH_AE[HoloCombatType.COMBAT_TYPE_RAID],
    ),
    HoloCombatType.COMBAT_TYPE_DMAX: DamageMultipliers(
        same_type_attack=BATTLE_SETTINGS.same_type_attack_bonus_multiplier,
        dodge_damage_reduction=BATTLE_SETTINGS.dodge_damage_reduction_percent,
        weather_attack=WEATHER_BONUS_SETTINGS.attack_bonus_multiplier,
        friendship_attack=FRIENDSHIP_DMG_BONUS,
        shadow_pokemon_attack=BATTLE_SETTINGS.shadow_pokemon_attack_bonus_multiplier,
        shadow_pokemon_defense=BATTLE_SETTINGS.shadow_pokemon_defense_bonus_multiplier,
        purified_pokemon_attack=BATTLE_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow,
        remote_attack=RAID_SETTINGS.remote_damage_modifier,
        same_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_same_type,
        different_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_different_type,
        blade_ae_attack=BEHEMOTH_BLADE_AE[HoloCombatType.COMBAT_TYPE_DMAX],
        bash_ae_defense=BEHEMOTH_BASH_AE[HoloCombatType.COMBAT_TYPE_DMAX],
    ),
    HoloCombatType.COMBAT_TYPE_GMAX: DamageMultipliers(
        same_type_attack=BATTLE_SETTINGS.same_type_attack_bonus_multiplier,
        dodge_damage_reduction=BATTLE_SETTINGS.dodge_damage_reduction_percent,
        weather_attack=WEATHER_BONUS_SETTINGS.attack_bonus_multiplier,
        friendship_attack=FRIENDSHIP_DMG_BONUS,
        shadow_pokemon_attack=BATTLE_SETTINGS.shadow_pokemon_attack_bonus_multiplier,
        shadow_pokemon_defense=BATTLE_SETTINGS.shadow_pokemon_defense_bonus_multiplier,
        purified_pokemon_attack=BATTLE_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow,
        remote_attack=RAID_SETTINGS.remote_damage_modifier,
        same_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_same_type,
        different_type_mega_attack=MEGA_EVO_SETTINGS.attack_boost_from_mega_different_type,
        blade_ae_attack=BEHEMOTH_BLADE_AE[HoloCombatType.COMBAT_TYPE_GMAX],
        bash_ae_defense=BEHEMOTH_BASH_AE[HoloCombatType.COMBAT_TYPE_GMAX],
    )
}


def get_mega_boost(
    combat_type: HoloCombatType,
    move_type: HoloPokemonType,
    mega_boosted_types: tuple[HoloPokemonType] | None,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    if not mega_boosted_types:
        return 1.0
    return mults.same_type_mega_attack if move_type in mega_boosted_types else mults.different_type_mega_attack

def get_purified_attack_bonus(
    combat_type: HoloCombatType,
    purified_attacker: bool,
    shadow_target: bool,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.purified_pokemon_attack if purified_attacker and shadow_target else 1.0

def get_shadow_attack_bonus(
    combat_type: HoloCombatType,
    shadow_attacker: bool,
    shadow_target: bool,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    shadow_attack_bonus = mults.shadow_pokemon_attack if shadow_attacker else 1.0
    shadow_defense_bonus = mults.shadow_pokemon_defense if shadow_target else 1.0
    return f32(shadow_attack_bonus / shadow_defense_bonus)

def get_weather_boost(
    combat_type: HoloCombatType,
    move_type: HoloPokemonType,
    weather_id: HoloWeatherCondition,
) -> float:
    if not weather_id:
        return 1.0
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.weather_attack if move_type in WEATHER[weather_id].pokemon_type else 1.0

def get_stab(
    combat_type: HoloCombatType,
    move_type: HoloPokemonType,
    atk_type_1: HoloPokemonType,
    atk_type_2: HoloPokemonType,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.same_type_attack if move_type == atk_type_1 or move_type == atk_type_2 else 1.0

def get_fiendship_boost(
    combat_type: HoloCombatType,
    friend_level: HoloFriendshipLevel,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.friendship_attack[friend_level] if mults.friendship_attack and friend_level else 1.0

def get_effect(
    move_type: HoloPokemonType,
    def_type_1: HoloPokemonType,
    def_type_2: HoloPokemonType = HoloPokemonType(0),
) -> float:
    if not move_type:
        return 1.0
    if not def_type_2:
        return TYPES[move_type].attack_scalar[def_type_1 - 1] if def_type_1 else 1.0
    return get_effect(move_type, def_type_1) * get_effect(move_type, def_type_2)

def get_fast_boost(combat_type: HoloCombatType, fast: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.fast_attack if fast else 1.0

def get_charge_boost(combat_type: HoloCombatType, charge: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.charge_attack if charge else 1.0

def get_dodge_boost(combat_type: HoloCombatType, dodged: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return f32(1.0 - mults.dodge_damage_reduction) if dodged else 1.0

def get_remote_boost(combat_type: HoloCombatType, remote: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.remote_attack if remote else 1.0

def get_blade_bash_boost(combat_type: HoloCombatType, blade: bool, bash: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    attack_bonus = mults.blade_ae_attack if blade else 1.0
    defense_bonus = mults.bash_ae_defense if bash else 1.0
    return f32(attack_bonus / defense_bonus)

def damage_formula(
    attacker: Pokemon,
    target: Pokemon,
    move_settings: MoveSettings | CombatMove,
    move_pos: int,
    dodged: bool,
    state: BattleState,
) -> int:
    move_power = move_settings.power
    move_type = (
        move_settings.pokemon_type
        if isinstance(move_settings, MoveSettings)
        else move_settings.type
    )

    base_damage = damage_formula_raw(
        attacker,
        target,
        move_power,
        move_type,
        move_pos,
        dodged,
        state,
    )

    return int(f32(base_damage + 1.0))

def damage_formula_raw(
    attacker: Pokemon,
    target: Pokemon,
    move_power: float,
    move_type: HoloPokemonType,
    move_pos: int,
    dodged: bool,
    state: BattleState,
) -> float:
    assert attacker.pokemon_settings and attacker.cpm
    assert target.pokemon_settings and target.cpm

    atk_stat, _, _ = (
        get_tgr_stats(
            attacker.pokemon_settings,
            attacker.cpm,
            target.tgr_member,
            attacker.atk_iv,
            attacker.def_iv,
            attacker.sta_iv,
        )
        if attacker.tgr_member
        else get_stats(
            attacker.pokemon_settings,
            attacker.cpm,
            attacker.atk_iv,
            attacker.def_iv,
            attacker.sta_iv,
        )
    )
    _, def_stat, _ = (
        get_tgr_stats(
            target.pokemon_settings,
            target.cpm,
            target.tgr_member,
            target.atk_iv,
            target.def_iv,
            target.sta_iv,
        )
        if target.tgr_member
        else get_stats(
            target.pokemon_settings,
            target.cpm,
            target.atk_iv,
            target.def_iv,
            target.sta_iv,
        )
    )

    attack_ratio = f32(f32(f32(atk_stat) * move_power) / f32(def_stat))

    multipliers = [
        get_mega_boost(state.combat_type, move_type, state.mega_boosted_types),
        get_purified_attack_bonus(state.combat_type, attacker.purified, target.shadow),
        get_shadow_attack_bonus(state.combat_type, attacker.shadow, target.shadow),
        get_weather_boost(state.combat_type, move_type, state.weather_id),
        get_stab(state.combat_type, move_type, attacker.pokemon_settings.type, attacker.pokemon_settings.type_2),
        get_fiendship_boost(state.combat_type, state.friendship_level),
        get_effect(move_type, target.pokemon_settings.type, target.pokemon_settings.type_2),
        get_fast_boost(state.combat_type, move_pos == 0),
        get_charge_boost(state.combat_type, move_pos > 0),
        get_dodge_boost(state.combat_type, dodged),
        get_remote_boost(state.combat_type, state.remote_raid),
        get_blade_bash_boost(state.combat_type, state.blade_ae, state.bash_ae),
        attack_ratio,
        0.5,
    ]

    return reduce(lambda a, b: f32(a * b), multipliers, 1.0)
