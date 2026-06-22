from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum

from proto.message import Message


class Action(IntEnum):
    ADD = 1
    SET = 2
    DEL = 3


@dataclass(frozen=True)
class Override:
    action_type: Action
    template_id: tuple[str, ...]
    target: list[str]
    value: list[str | Message]

    @classmethod
    def from_message(cls, msg: Message) -> Override:
        return cls(
            action_type=msg.get_enum("action_type", Action),
            template_id=msg.get_string_list("template_id"),
            target=msg.get_string("target").strip('"').split('.'),
            value=msg.get("value"),
        )

@dataclass(frozen=True)
class RemTemplate:
    template_id: tuple[str, ...]

    @classmethod
    def from_message(cls, msg: Message) -> RemTemplate:
        return cls(
            template_id=msg.get_string_list("template_id"),
        )
