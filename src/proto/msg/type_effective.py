from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class TypeEffective:
    attack_scalar: tuple[float, ...]
    attack_type: str

    @classmethod
    def from_message(cls, msg: Message) -> TypeEffective:
        return cls(
            attack_scalar=msg.get_float_list("attackScalar"),
            attack_type=msg.get_string("attackType"),
        )
