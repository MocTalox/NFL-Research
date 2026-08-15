from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class RaidSettings:
    remote_damage_modifier: float

    @classmethod
    def from_message(cls, msg: Message) -> RaidSettings:
        return cls(
            remote_damage_modifier=msg.get_float("remoteDamageModifier"),
        )
