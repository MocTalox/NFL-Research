from __future__ import annotations

from dataclasses import dataclass

from nfl.data import Message
from nfl.proto import HoloPokemonType, HoloWeatherCondition


@dataclass(frozen=True)
class WeatherAffinities:
    weather_condition: HoloWeatherCondition
    pokemon_type: tuple[HoloPokemonType, ...]

    @classmethod
    def from_message(cls, msg: Message) -> WeatherAffinities:
        return cls(
            weather_condition=msg.get_enum("weatherCondition", HoloWeatherCondition),
            pokemon_type=msg.get_enum_list("pokemonType", HoloPokemonType),
        )
