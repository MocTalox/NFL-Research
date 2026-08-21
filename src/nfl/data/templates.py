from collections.abc import Callable
from typing import TypeVar

from nfl.exceptions import ConfigurationError
from nfl.io import Message, get_templates
from nfl.proto import (
    BattleSettings,
    BreadMoveMappings,
    BreadPokemonScalingSettings,
    CombatMove,
    CombatSettings,
    CombatStatStageSettings,
    ContestSettings,
    FormSettings,
    FriendshipMilestoneSettings,
    LocationCardSettings,
    MegaEvoSettings,
    MoveSettings,
    NonCombatMoveSettings,
    PlayerLevel,
    PokemonExtendedSettings,
    PokemonFamily,
    PokemonSettings,
    RaidSettings,
    RocketSettings,
    SourdoughMoveMappingSettings,
    StationedPokemonTableSettings,
    TemporaryEvolutionSettings,
    TypeEffective,
    WeatherAffinities,
    WeatherBonusSettings,
)

T = TypeVar("T")


def _load_set(key: str, constructor: Callable[[Message], T]) -> set[T]:
    try:
        elements = {
            constructor(template.value) for template in get_templates(key).values()
        }

    except ValueError as e:
        raise ConfigurationError("Configured game master is invalid") from e

    return elements


def _load_elem(key: str, constructor: Callable[[Message], T]) -> T:
    try:
        elements = [
            constructor(template.value) for template in get_templates(key).values()
        ]

        if len(elements) != 1:
            raise ValueError(f"Multiple or none templates for key: {key}")

    except ValueError as e:
        raise ConfigurationError("Configured game master is invalid") from e

    return elements[0]


BATTLE_SETTINGS = _load_elem(
    "battle_settings",
    BattleSettings.from_message,
)

BREAD_MOVE_MAPPINGS = _load_elem(
    "breadMoveMappings",
    BreadMoveMappings.from_message,
)

BREAD_POKEMON_SCALING_SETTINGS = _load_elem(
    "breadPokemonScalingSettings",
    BreadPokemonScalingSettings.from_message,
)

COMBAT_MOVE = _load_set(
    "combat_move",
    CombatMove.from_message,
)

COMBAT_SETTINGS = _load_elem(
    "combatSettings",
    CombatSettings.from_message,
)

COMBAT_STAT_STAGE_SETTINGS = _load_elem(
    "combat_stat_stage_settings",
    CombatStatStageSettings.from_message,
)

CONTEST_SETTINGS = _load_elem(
    "contestSettings",
    ContestSettings.from_message,
)

FORM_SETTINGS = _load_set(
    "formSettings",
    FormSettings.from_message,
)

FRIENDSHIP_MILESTONE_SETTINGS = _load_set(
    "friendshipMilestoneSettings",
    FriendshipMilestoneSettings.from_message,
)

LOCATION_CARD_SETTINGS = _load_set(
    "locationCardSettings",
    LocationCardSettings.from_message,
)

MEGA_EVO_SETTINGS = _load_elem(
    "mega_evo_settings",
    MegaEvoSettings.from_message,
)

MOVE_SETTINGS = _load_set(
    "moveSettings",
    MoveSettings.from_message,
)

NON_COMBAT_MOVE_SETTINGS = _load_set(
    "nonCombatMoveSettings",
    NonCombatMoveSettings.from_message,
)

PLAYER_LEVEL = _load_elem(
    "playerLevel",
    PlayerLevel.from_message,
)

POKEMON_EXTENDED_SETTINGS = _load_set(
    "pokemonExtendedSettings",
    PokemonExtendedSettings.from_message,
)

POKEMON_FAMILY = _load_set(
    "pokemonFamily",
    PokemonFamily.from_message,
)

POKEMON_SETTINGS = _load_set(
    "pokemonSettings",
    PokemonSettings.from_message,
)

RAID_SETTINGS = _load_elem(
    "raidSettings",
    RaidSettings.from_message,
)

ROCKET_SETTINGS = _load_elem(
    "rocket_settings",
    RocketSettings.from_message,
)

SOURDOUGH_MOVE_MAPPING_SETTINGS = _load_elem(
    "sourdoughMoveMappingSettings",
    SourdoughMoveMappingSettings.from_message,
)

STATIONED_POKEMON_TABLE_SETTINGS = _load_elem(
    "stationedPokemonTableSettings",
    StationedPokemonTableSettings.from_message,
)

TEMPORARY_EVOLUTION_SETTINGS = _load_set(
    "temporaryEvolutionSettings",
    TemporaryEvolutionSettings.from_message,
)

TYPE_EFFECTIVE = _load_set(
    "type_effective",
    TypeEffective.from_message,
)

WEATHER_AFFINITIES = _load_set(
    "weather_affinities",
    WeatherAffinities.from_message,
)

WEATHER_BONUS_SETTINGS = _load_elem(
    "weather_bonus_settings",
    WeatherBonusSettings.from_message,
)
