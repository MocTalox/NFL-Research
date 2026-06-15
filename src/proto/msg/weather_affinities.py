from __future__ import annotations
from dataclasses import dataclass
from core.gm_holoholo import HoloPokemonType
from proto.message import Message


@dataclass(frozen=True)
class WeatherAffinities:
    weather_condition: str
    pokemon_type: tuple[HoloPokemonType, ...]

    @classmethod
    def from_message(cls, msg: Message) -> WeatherAffinities:
        return cls(
            weather_condition=msg.get_string("weatherCondition"),
            pokemon_type=msg.get_enum_list("pokemonType", HoloPokemonType),
        )
