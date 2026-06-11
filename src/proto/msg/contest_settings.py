from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class ContestSettings:
    contest_score_coefficient: ContestScoreCoefficient

    @classmethod
    def from_message(cls, msg: Message) -> ContestSettings:
        return cls(
            contest_score_coefficient=msg.get_object("contestScoreCoefficient", ContestScoreCoefficient.from_message),
        )

@dataclass(frozen=True)
class ContestScoreCoefficient:
    pokemon_size: PokemonSize

    @classmethod
    def from_message(cls, msg: Message) -> ContestScoreCoefficient:
        return cls(
            pokemon_size=msg.get_object("pokemonSize", PokemonSize.from_message),
        )

@dataclass(frozen=True)
class PokemonSize:
    height_coefficient: int
    weight_coefficient: int
    iv_coefficient: int
    xxl_adjustment_factor: int

    @classmethod
    def from_message(cls, msg: Message) -> PokemonSize:
        return cls(
            height_coefficient=msg.get_int("heightCoefficient"),
            weight_coefficient=msg.get_int("weightCoefficient"),
            iv_coefficient=msg.get_int("ivCoefficient"),
            xxl_adjustment_factor=msg.get_int("xxlAdjustmentFactor"),
        )
