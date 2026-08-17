from __future__ import annotations

from dataclasses import dataclass

from nfl.data import Message


@dataclass(frozen=True)
class MegaEvoSettings:
    attack_boost_from_mega_different_type: float
    attack_boost_from_mega_same_type: float

    @classmethod
    def from_message(cls, msg: Message) -> MegaEvoSettings:
        return cls(
            attack_boost_from_mega_different_type=msg.get_float(
                "attackBoostFromMegaDifferentType"
            ),
            attack_boost_from_mega_same_type=msg.get_float(
                "attackBoostFromMegaSameType"
            ),
        )
