from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class PlayerLevel:
    cp_multiplier: tuple[float, ...]

    @classmethod
    def from_message(cls, msg: Message) -> PlayerLevel:
        return cls(
            cp_multiplier=msg.get_float_list("cpMultiplier"),
        )
