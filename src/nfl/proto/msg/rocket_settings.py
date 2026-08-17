from __future__ import annotations

from dataclasses import dataclass

from nfl.proto import HoloCharacterCategory, Message


@dataclass(frozen=True)
class RocketSettings:
    cp_multiplier: tuple[float, ...]
    rank: tuple[Rank, ...]

    @classmethod
    def from_message(cls, msg: Message) -> RocketSettings:
        return cls(
            cp_multiplier=msg.get_float_list("cpMultiplier"),
            rank=msg.get_object_list("rank", Rank.from_message),
        )


@dataclass(frozen=True)
class Rank:
    character_category: HoloCharacterCategory
    rank_multiplier: float

    @classmethod
    def from_message(cls, msg: Message) -> Rank:
        return cls(
            character_category=msg.get_enum(
                "character_category", HoloCharacterCategory
            ),
            rank_multiplier=msg.get_float("rank_multiplier"),
        )
