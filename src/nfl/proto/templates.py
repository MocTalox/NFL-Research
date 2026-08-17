from typing import Callable, TypeVar

from nfl.data import get_templates

from .message import Message
from .msg.battle_settings import BattleSettings
from .msg.bread_move_mappings import BreadMoveMappings
from .msg.bread_pokemon_scaling_settings import BreadPokemonScalingSettings
from .msg.combat_move import CombatMove
from .msg.combat_settings import CombatSettings
from .msg.combat_stat_stage_settings import CombatStatStageSettings
from .msg.contest_settings import ContestSettings
from .msg.form_settings import FormSettings
from .msg.friendship_milestone_settings import FriendshipMilestoneSettings
from .msg.mega_evo_settings import MegaEvoSettings
from .msg.move_settings import MoveSettings
from .msg.non_combat_move_settings import NonCombatMoveSettings
from .msg.player_level import PlayerLevel
from .msg.pokemon_extended_settings import PokemonExtendedSettings
from .msg.pokemon_family import PokemonFamily
from .msg.pokemon_settings import PokemonSettings
from .msg.raid_settings import RaidSettings
from .msg.rocket_settings import RocketSettings
from .msg.sourdough_move_mapping_settings import SourdoughMoveMappingSettings
from .msg.stationed_pokemon_table_settings import StationedPokemonTableSettings
from .msg.temporary_evolution_settings import TemporaryEvolutionSettings
from .msg.type_effective import TypeEffective
from .msg.weather_affinities import WeatherAffinities
from .msg.weather_bonus_settings import WeatherBonusSettings


T = TypeVar("T")


def _load_set(key: str, constructor: Callable[[Message], T]) -> set[T]:
    elements = {
        constructor(template.value)
        for template in get_templates(key).values()
    }

    return elements

def _load_elem(key: str, constructor: Callable[[Message], T]) -> T:
    elements = [
        constructor(template.value)
        for template in get_templates(key).values()
    ]

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
