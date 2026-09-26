from dataclasses import dataclass, field
from functools import reduce
from typing import Literal, overload

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
    is_tgr_member,
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

from .stats import get_stats, get_tgr_stats


@dataclass
class DummyPokemon:
    base_atk: int
    base_def: int
    base_sta: int
    type_1: HoloPokemonType
    type_2: HoloPokemonType
    alignment: HoloAlignment


@dataclass
class DummyMove:
    power: int
    type: HoloPokemonType


@dataclass
class BattlePokemon:
    pokemon: PokeSpecies | DummyPokemon
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


def get_dodge_boost(combat_type: HoloCombatType, is_dodged: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return f32(1.0 - mults.dodge_damage_reduction) if is_dodged else 1.0


def get_remote_boost(combat_type: HoloCombatType, remote: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    return mults.remote_attack if remote else 1.0


def get_blade_bash_boost(combat_type: HoloCombatType, blade: bool, bash: bool) -> float:
    mults = _DAMAGE_MULTIPLIERS[combat_type]
    attack_bonus = mults.blade_ae_attack if blade else 1.0
    defense_bonus = mults.bash_ae_defense if bash else 1.0
    return f32(attack_bonus / defense_bonus)


@overload
def calc_damage(
    state: BattleState,
    attacker: BattlePokemon,
    target: BattlePokemon,
    move_data: MoveSettings | CombatMove | DummyMove,
    is_charge_move: bool = False,
    is_dodged: bool = False,
    rounded: Literal[True] = True,
) -> int: ...


@overload
def calc_damage(
    state: BattleState,
    attacker: BattlePokemon,
    target: BattlePokemon,
    move_data: MoveSettings | CombatMove | DummyMove,
    is_charge_move: bool = False,
    is_dodged: bool = False,
    rounded: Literal[False] = False,
) -> float: ...


def calc_damage(
    state: BattleState,
    attacker: BattlePokemon,
    target: BattlePokemon,
    move_data: MoveSettings | CombatMove | DummyMove,
    is_charge_move: bool = False,
    is_dodged: bool = False,
    rounded: bool = True,
) -> int | float:
    if attacker.cpm <= 0 or target.cpm <= 0:
        raise ValidationError(
            "INVALID_CPM_VALUES", attacker_cpm=attacker.cpm, target_cpm=target.cpm
        )

    move_power = move_data.power
    move_type = (
        move_data.pokemon_type
        if isinstance(move_data, MoveSettings)
        else move_data.type
    )

    atk_stat, _, _, atk_type_1, atk_type_2 = _get_pokemon_stats(attacker)
    _, def_stat, _, tar_type_1, tar_type_2 = _get_pokemon_stats(target)
    atk_alignment = attacker.pokemon.alignment
    tar_alignment = target.pokemon.alignment

    attack_ratio = f32(f32(f32(atk_stat) * move_power) / f32(def_stat))

    multipliers = [
        get_mega_boost(state.combat_type, move_type, state.mega_boosted_types),
        get_shadow_attack_bonus(state.combat_type, atk_alignment, tar_alignment),
        get_weather_boost(state.combat_type, move_type, state.weather_id),
        get_stab(state.combat_type, move_type, atk_type_1, atk_type_2),
        get_fiendship_boost(state.combat_type, state.friendship_level),
        get_effect(move_type, tar_type_1, tar_type_2),
        get_fast_boost(state.combat_type, not is_charge_move),
        get_charge_boost(state.combat_type, is_charge_move),
        get_dodge_boost(state.combat_type, is_dodged),
        get_remote_boost(state.combat_type, state.remote_raid),
        get_helpers_boost(state.combat_type, state.num_helpers),
        get_blade_bash_boost(state.combat_type, state.blade_ae, state.bash_ae),
        attack_ratio,
        0.5,
    ]

    base_damage = reduce(lambda a, b: f32(a * b), multipliers, 1.0)

    return int(f32(base_damage + 1.0)) if rounded else base_damage


def _get_pokemon_stats(battle_pokemon: BattlePokemon):
    if isinstance(battle_pokemon.pokemon, DummyPokemon):
        type_1, type_2 = battle_pokemon.pokemon.type_1, battle_pokemon.pokemon.type_2

        if is_tgr_member(battle_pokemon.owner):
            atk_stat, def_stat, sta_stat = get_tgr_stats(
                base_atk=battle_pokemon.pokemon.base_atk,
                base_def=battle_pokemon.pokemon.base_def,
                base_sta=battle_pokemon.pokemon.base_sta,
                rcpm=battle_pokemon.cpm,
                enemy=battle_pokemon.owner,
                iv_atk=battle_pokemon.atk_iv,
                iv_def=battle_pokemon.def_iv,
                iv_sta=battle_pokemon.sta_iv,
            )
        else:
            atk_stat, def_stat, sta_stat = get_stats(
                base_atk=battle_pokemon.pokemon.base_atk,
                base_def=battle_pokemon.pokemon.base_def,
                base_sta=battle_pokemon.pokemon.base_sta,
                cpm=battle_pokemon.cpm,
                iv_atk=battle_pokemon.atk_iv,
                iv_def=battle_pokemon.def_iv,
                iv_sta=battle_pokemon.sta_iv,
            )
    else:
        pokemon_settings = get_pokemon_settings(battle_pokemon.pokemon)
        type_1, type_2 = pokemon_settings.type, pokemon_settings.type_2

        if is_tgr_member(battle_pokemon.owner):
            atk_stat, def_stat, sta_stat = get_tgr_stats(
                poke=battle_pokemon.pokemon,
                rcpm=battle_pokemon.cpm,
                enemy=battle_pokemon.owner,
                iv_atk=battle_pokemon.atk_iv,
                iv_def=battle_pokemon.def_iv,
                iv_sta=battle_pokemon.sta_iv,
            )
        else:
            atk_stat, def_stat, sta_stat = get_stats(
                poke=battle_pokemon.pokemon,
                cpm=battle_pokemon.cpm,
                iv_atk=battle_pokemon.atk_iv,
                iv_def=battle_pokemon.def_iv,
                iv_sta=battle_pokemon.sta_iv,
            )

    return atk_stat, def_stat, sta_stat, type_1, type_2
