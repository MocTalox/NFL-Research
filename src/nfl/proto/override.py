from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from nfl.utils.raw_value import RawValue

from .message import Message


class Action(IntEnum):
    ADD = 1
    SET = 2
    DEL = 3


@dataclass(frozen=True)
class Override:
    action_type: Action
    template_id: tuple[str, ...]
    target: list[str]
    value: list[str | RawValue | Message]

    @classmethod
    def from_message(cls, msg: Message) -> Override:
        return cls(
            action_type=msg.get_enum("action_type", Action),
            template_id=msg.get_string_list("template_id"),
            target=msg.get_string("target").split("."),
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


@dataclass(frozen=True)
class AddTemplate:
    template_id: str
    key: str
    value: list[str | RawValue | Message]

    @classmethod
    def from_message(cls, msg: Message) -> AddTemplate:
        return cls(
            template_id=msg.get_string("template_id"),
            key=msg.get_string("key"),
            value=msg.get("value"),
        )
