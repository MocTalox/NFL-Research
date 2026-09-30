from dataclasses import dataclass

from nfl.data import PokeSpecies
from nfl.proto import (
    HoloAlignment,
    HoloCharacterCategory,
    HoloCombatType,
    HoloFriendshipLevel,
    HoloPokemonType,
    HoloWeatherCondition,
)


@dataclass
class BattleState:
    combat_type: HoloCombatType
    mega_boosted_types: tuple[HoloPokemonType, ...] | None = None
    weather_id: HoloWeatherCondition = HoloWeatherCondition.NONE
    friendship_level: HoloFriendshipLevel = HoloFriendshipLevel.FRIENDSHIP_LEVEL_UNSET
    remote_raid: bool = False
    num_helpers: int = 0
    blade_ae: bool = False
    bash_ae: bool = False


@dataclass
class BattleDummyPokemon:
    base_atk: int
    base_def: int
    base_sta: int
    type_1: HoloPokemonType
    type_2: HoloPokemonType
    alignment: HoloAlignment


@dataclass
class BattleDummyMove:
    power: int
    type: HoloPokemonType


@dataclass
class BattlePokemon:
    pokemon: PokeSpecies | BattleDummyPokemon
    atk_iv: int
    def_iv: int
    sta_iv: int
    cpm: float
    owner: HoloCharacterCategory = HoloCharacterCategory.UNSET
