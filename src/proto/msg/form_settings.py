from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class FormSettings:
    pokemon: str
    forms: tuple[Form, ...]
    ignore: bool

    @classmethod
    def from_message(cls, msg: Message) -> FormSettings:
        return cls(
            pokemon=msg.get_string("pokemon"),
            forms=msg.get_object_list("forms", Form.from_message),
            ignore=msg.get_bool_or_false("moc_ignore"),
        )

@dataclass(frozen=True)
class Form:
    form: str
    is_costume: bool
    ignore: bool

    @classmethod
    def from_message(cls, msg: Message) -> Form:
        return cls(
            form=msg.get_string("form"),
            is_costume=msg.get_bool_or_false("isCostume"),
            ignore=msg.get_bool_or_false("moc_ignore"),
        )
