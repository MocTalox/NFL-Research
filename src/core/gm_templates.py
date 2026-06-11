from typing import Callable, TypeVar

from core.gm_holoholo import GAME_MASTER
from proto.message import Message
from proto.msg.battle_settings import BattleSettings
from proto.msg.bread_move_mappings import BreadMoveMappings
from proto.msg.bread_pokemon_scaling_settings import BreadPokemonScalingSettings
from proto.msg.combat_move import CombatMove
from proto.msg.combat_settings import CombatSettings
from proto.msg.combat_stat_stage_settings import CombatStatStageSettings
from proto.msg.contest_settings import ContestSettings
from proto.msg.form_settings import FormSettings
from proto.msg.friendship_milestone_settings import FriendshipMilestoneSettings
from proto.msg.move_settings import MoveSettings
from proto.msg.player_level import PlayerLevel
from proto.msg.pokemon_extended_settings import PokemonExtendedSettings
from proto.msg.pokemon_family import PokemonFamily
from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.raid_settings import RaidSettings
from proto.msg.sourdough_move_mapping_settings import SourdoughMoveMappingSettings
from proto.msg.type_effective import TypeEffective
from proto.msg.weather_affinities import WeatherAffinities


T = TypeVar("T")


def _load_set(key: str, constructor: Callable[[Message], T]) -> set[T]:
    return {
        constructor(template.value)
        for template in GAME_MASTER[key].values()
    }

def _load_elem(key: str, constructor: Callable[[Message], T]) -> T:
    elements = [
        constructor(template.value)
        for template in GAME_MASTER[key].values()
    ]

    if len(elements) != 1:
        raise ValueError(
            f"Multiple or none templates for key: {key}"
        )

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

MOVE_SETTINGS = _load_set(
    "moveSettings",
    MoveSettings.from_message,
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

SOURDOUGH_MOVE_MAPPING_SETTINGS = _load_elem(
    "sourdoughMoveMappingSettings",
    SourdoughMoveMappingSettings.from_message,
)

TYPE_EFFECTIVE = _load_set(
    "type_effective",
    TypeEffective.from_message,
)

WEATHER_AFFINITIES = _load_set(
    "weather_affinities",
    WeatherAffinities.from_message,
)
