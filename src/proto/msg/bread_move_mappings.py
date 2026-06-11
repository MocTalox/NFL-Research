from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class BreadMoveMappings:
    mappings: tuple[Mappings, ...]

    @classmethod
    def from_message(cls, msg: Message) -> BreadMoveMappings:
        return cls(
            mappings=msg.get_object_list("mappings", Mappings.from_message),
        )

@dataclass(frozen=True)
class Mappings:
    type: str
    move: str

    @classmethod
    def from_message(cls, msg: Message) -> Mappings:
        return cls(
            type=msg.get_string("type"),
            move=msg.get_string("move"),
        )
