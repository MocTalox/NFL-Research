from dataclasses import dataclass, field
from functools import reduce

from nfl.data import (
    BATTLE_SETTINGS,
    BEHEMOTH_BASH_AE,
    BEHEMOTH_BLADE_AE,
    COMBAT_SETTINGS,
    FRIENDSHIP_DMG_BONUS,
    HELPERS_DMG_BONUS,
    MEGA_EVO_SETTINGS,
    RAID_SETTINGS,
    TYPES,
    WEATHER,
    WEATHER_BONUS_SETTINGS,
    PokeSpecies,
    get_pokemon_settings,
)
from nfl.exceptions import ValidationError
from nfl.proto import (
    CombatMove,
    HoloAlignment,
    HoloCharacterCategory,
    HoloCombatType,
    HoloFriendshipLevel,
    HoloPokemonType,
    HoloWeatherCondition,
    MoveSettings,
)
from nfl.utils import f32

from .stats import get_stats_raw, get_tgr_stats_raw


@dataclass
class BattlePokemon:
    pokemon: PokeSpecies
    atk_iv: int
    def_iv: int
    sta_iv: int
    cpm: float
    owner: HoloCharacterCategory = HoloCharacterCategory.UNSET


@dataclass
class BattleState:
    combat_type: HoloCombatType
    mega_boosted_types: tuple[HoloPokemonType] | None = None
    weather_id: HoloWeatherCondition = HoloWeatherCondition.NONE
    friendship_level: HoloFriendshipLevel = HoloFriendshipLevel.FRIENDSHIP_LEVEL_UNSET
    remote_raid: bool = False
    num_helpers: int = 0
    blade_ae: bool = False
    bash_ae: bool = False


@dataclass(frozen=True)
class _DamageMultipliers:
    fast_attack: float = 1.0
    charge_attack: float = 1.0
    same_type_attack: float = 1.0
    dodge_damage_reduction: float = 1.0
    weather_attack: float = 1.0
    friendship_attack: dict[HoloFriendshipLevel, float] = field(default_factory=dict)
    shadow_pokemon_attack: float = 1.0
    shadow_pokemon_defense: float = 1.0
    purified_pokemon_attack: float = 1.0  # vs shadow only (unused in-game)
    same_type_mega_attack: float = 1.0
    different_type_mega_attack: float = 1.0
    remote_attack: float = 1.0
    helpers_attack: dict[int, int] = field(default_factory=dict)
    blade_ae_attack: float = 1.0
    bash_ae_defense: float = 1.0


_DAMAGE_MULTIPLIERS = {
    HoloCombatType.VS_SEEKER: _DamageMultipliers(
        fast_attack=COMBAT_SETTINGS.fast_attack_bonus_multiplier,
        charge_attack=COMBAT_SETTINGS.charge_attack_bonus_multiplier,
        same_type_attack=COMBAT_SETTINGS.same_type_attack_bonus_multiplier,
        shadow_pokemon_attack=COMBAT_SETTINGS.shadow_pokemon_attack_bonus_multiplier,
        shadow_pokemon_defense=COMBAT_SETTINGS.shadow_pokemon_defense_bonus_multiplier,
        purified_pokemon_attack=COMBAT_SETTINGS.purified_pokemon_attack_multiplier_vs_shadow,
    ),
    HoloCombatType.SOLO: _DamageMultipliers(
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
    HoloCombatType.COMBAT_TYPE_RAID: _DamageMultipliers(
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
    HoloCombatType.COMBAT_TYPE_DMAX: _DamageMultipliers(
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
        helpers_attack=HELPERS_DMG_BONUS,
        blade_ae_attack=BEHEMOTH_BLADE_AE[HoloCombatType.COMBAT_TYPE_DMAX],
        bash_ae_defense=BEHEMOTH_BASH_AE[HoloCombatType.COMBAT_TYPE_DMAX],
    ),
    HoloCombatType.COMBAT_TYPE_GMAX: _DamageMultipliers(
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
        helpers_attack=HELPERS_DMG_BONUS,
        blade_ae_attack=BEHEMOTH_BLADE_AE[HoloCombatType.COMBAT_TYPE_GMAX],
        bash_ae_defense=BEHEMOTH_BASH_AE[HoloCombatType.COMBAT_TYPE_GMAX],
    ),
}


def get_mega_boost(
    combat_type: HoloCombatType,
    move_type: HoloPokemonType,
    mega_boosted_types: tuple[HoloPokemonType] | None,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    if not mega_boosted_types:
        return 1.0
    return (
        mults.same_type_mega_attack
        if move_type in mega_boosted_types
        else mults.different_type_mega_attack
    )


def get_shadow_attack_bonus(
    combat_type: HoloCombatType,
    attacker_alignment: HoloAlignment,
    target_alignment: HoloAlignment,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    shadow_attack_bonus = (
        mults.shadow_pokemon_attack
        if attacker_alignment == HoloAlignment.SHADOW
        else 1.0
    )
    shadow_defense_bonus = (
        mults.shadow_pokemon_defense
        if target_alignment == HoloAlignment.SHADOW
        else 1.0
    )
    purified_attack_bonus = (
        mults.purified_pokemon_attack
        if attacker_alignment == HoloAlignment.PURIFIED
        and target_alignment == HoloAlignment.SHADOW
        else 1.0
    )
    return f32(shadow_attack_bonus / shadow_defense_bonus * purified_attack_bonus)


def get_weather_boost(
    combat_type: HoloCombatType,
    move_type: HoloPokemonType,
    weather_id: HoloWeatherCondition,
) -> float:
    if not weather_id:
        return 1.0
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return (
        mults.weather_attack if move_type in WEATHER[weather_id].pokemon_type else 1.0
    )


def get_stab(
    combat_type: HoloCombatType,
    move_type: HoloPokemonType,
    atk_type_1: HoloPokemonType,
    atk_type_2: HoloPokemonType,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return (
        mults.same_type_attack
        if move_type == atk_type_1 or move_type == atk_type_2
        else 1.0
    )


def get_fiendship_boost(
    combat_type: HoloCombatType,
    friend_level: HoloFriendshipLevel,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return (
        mults.friendship_attack[friend_level]
        if mults.friendship_attack and friend_level
        else 1.0
    )


def get_helpers_boost(
    combat_type: HoloCombatType,
    num_helpers: int,
) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return (  # TODO hardcoded 20 length
        1 + mults.helpers_attack[min(20, num_helpers)] / 10000
        if mults.helpers_attack and num_helpers
        else 1.0
    )


def get_effect(
    move_type: HoloPokemonType,
    def_type_1: HoloPokemonType,
    def_type_2: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE,
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


# TODO its a bit sus that this one accepts settings rather than name but ok...
def calc_damage(
    attacker: BattlePokemon,
    target: BattlePokemon,
    move_settings: MoveSettings | CombatMove,
    charged_move: bool,
    dodged: bool,
    state: BattleState,
) -> int:
    move_power = move_settings.power
    move_type = (
        move_settings.pokemon_type
        if isinstance(move_settings, MoveSettings)
        else move_settings.type
    )

    base_damage = calc_damage_raw(
        attacker,
        target,
        move_power,
        move_type,
        charged_move,
        dodged,
        state,
    )

    return int(f32(base_damage + 1.0))


def calc_damage_raw(
    attacker: BattlePokemon,
    target: BattlePokemon,
    move_power: float,
    move_type: HoloPokemonType,
    charged_move: bool,
    dodged: bool,
    state: BattleState,
) -> float:
    if attacker.cpm <= 0 or target.cpm <= 0:
        raise ValidationError()  # TODO err msg

    attacker_pokemon_settings = get_pokemon_settings(attacker.pokemon)
    target_pokemon_settings = get_pokemon_settings(target.pokemon)

    atk_stat, _, _ = (
        get_tgr_stats_raw(
            attacker_pokemon_settings,
            attacker.cpm,
            target.owner,
            attacker.atk_iv,
            attacker.def_iv,
            attacker.sta_iv,
        )
        if attacker.owner
        else get_stats_raw(
            attacker_pokemon_settings,
            attacker.cpm,
            attacker.atk_iv,
            attacker.def_iv,
            attacker.sta_iv,
        )
    )
    _, def_stat, _ = (
        get_tgr_stats_raw(
            target_pokemon_settings,
            target.cpm,
            target.owner,
            target.atk_iv,
            target.def_iv,
            target.sta_iv,
        )
        if target.owner
        else get_stats_raw(
            target_pokemon_settings,
            target.cpm,
            target.atk_iv,
            target.def_iv,
            target.sta_iv,
        )
    )

    attack_ratio = f32(f32(f32(atk_stat) * move_power) / f32(def_stat))

    multipliers = [
        get_mega_boost(state.combat_type, move_type, state.mega_boosted_types),
        get_shadow_attack_bonus(
            state.combat_type, attacker.pokemon.alignment, target.pokemon.alignment
        ),
        get_weather_boost(state.combat_type, move_type, state.weather_id),
        get_stab(
            state.combat_type,
            move_type,
            attacker_pokemon_settings.type,
            attacker_pokemon_settings.type_2,
        ),
        get_fiendship_boost(state.combat_type, state.friendship_level),
        get_effect(
            move_type, target_pokemon_settings.type, target_pokemon_settings.type_2
        ),
        get_fast_boost(state.combat_type, not charged_move),
        get_charge_boost(state.combat_type, charged_move),
        get_dodge_boost(state.combat_type, dodged),
        get_remote_boost(state.combat_type, state.remote_raid),
        get_helpers_boost(state.combat_type, state.num_helpers),
        get_blade_bash_boost(state.combat_type, state.blade_ae, state.bash_ae),
        attack_ratio,
        0.5,
    ]

    return reduce(lambda a, b: f32(a * b), multipliers, 1.0)
