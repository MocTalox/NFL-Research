from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class WeatherAffinities:
    weather_condition: str
    pokemon_type: tuple[str, ...]

    @classmethod
    def from_message(cls, msg: Message) -> WeatherAffinities:
        return cls(
            weather_condition=msg.get_string("weatherCondition"),
            pokemon_type=msg.get_string_list("pokemonType"),
        )
