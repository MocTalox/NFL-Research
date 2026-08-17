from collections.abc import Callable
from typing import TypeVar

from nfl.data import get_templates

from .message import Message

# Import the complete messages collection intentionally:
# this module operates on every public dataclass in msg.
from .msg import *

T = TypeVar("T")


def _load_set(key: str, constructor: Callable[[Message], T]) -> set[T]:
    elements = {constructor(template.value) for template in get_templates(key).values()}

    return elements


def _load_elem(key: str, constructor: Callable[[Message], T]) -> T:
    elements = [constructor(template.value) for template in get_templates(key).values()]

    if len(elements) != 1:
        raise ValueError(f"Multiple or none templates for key: {key}")

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


__all__ = [
    "BATTLE_SETTINGS",
    "BREAD_MOVE_MAPPINGS",
    "BREAD_POKEMON_SCALING_SETTINGS",
    "COMBAT_MOVE",
    "COMBAT_SETTINGS",
    "COMBAT_STAT_STAGE_SETTINGS",
    "CONTEST_SETTINGS",
    "FORM_SETTINGS",
    "FRIENDSHIP_MILESTONE_SETTINGS",
    "MEGA_EVO_SETTINGS",
    "MOVE_SETTINGS",
    "NON_COMBAT_MOVE_SETTINGS",
    "PLAYER_LEVEL",
    "POKEMON_EXTENDED_SETTINGS",
    "POKEMON_FAMILY",
    "POKEMON_SETTINGS",
    "RAID_SETTINGS",
    "ROCKET_SETTINGS",
    "SOURDOUGH_MOVE_MAPPING_SETTINGS",
    "STATIONED_POKEMON_TABLE_SETTINGS",
    "TEMPORARY_EVOLUTION_SETTINGS",
    "TYPE_EFFECTIVE",
    "WEATHER_AFFINITIES",
    "WEATHER_BONUS_SETTINGS",
]
