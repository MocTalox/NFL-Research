from dataclasses import dataclass

from nfl.data import PokeSpecies
from nfl.proto import (
    HoloAlignment,
    HoloCharacterCategory,
    HoloCombatType,
    HoloFriendshipLevel,
    HoloPokemonType,
    HoloTempEvoId,
    HoloWeatherCondition,
)


@dataclass
class BattleState:
    combat_type: HoloCombatType
    temp_evo_level: int = 0
    mega_boosted_types: tuple[HoloPokemonType, ...] | None = None
    weather_id: HoloWeatherCondition = HoloWeatherCondition.NONE
    friendship_level: HoloFriendshipLevel = HoloFriendshipLevel.FRIENDSHIP_LEVEL_UNSET
    remote_raid: bool = False
    num_helpers: int = 0
    blade_ae: bool = False
    bash_ae: bool = False
    mega_ae: bool = False


@dataclass
class BattleDummyPokemon:
    base_atk: int = 0
    base_def: int = 0
    base_sta: int = 0
    type_1: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE
    type_2: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE
    temp_evo: HoloTempEvoId = HoloTempEvoId.TEMP_EVOLUTION_UNSET
    alignment: HoloAlignment = HoloAlignment.ALIGNMENT_UNSET


@dataclass
class BattleDummyMove:
    power: float = 0.0
    type: HoloPokemonType = HoloPokemonType.POKEMON_TYPE_NONE


@dataclass
class BattlePokemon:
    pokemon: PokeSpecies | BattleDummyPokemon
    atk_iv: int = 0
    def_iv: int = 0
    sta_iv: int = 0
    cpm: float = 0.0
    owner: HoloCharacterCategory = HoloCharacterCategory.UNSET
