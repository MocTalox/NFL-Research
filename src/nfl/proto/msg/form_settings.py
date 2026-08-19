from __future__ import annotations

from dataclasses import dataclass

from nfl.io import Message
from nfl.proto import HoloPokemonForm, HoloPokemonId


@dataclass(frozen=True)
class FormSettings:
    pokemon: HoloPokemonId
    forms: tuple[Form, ...]
    ignore: bool

    @classmethod
    def from_message(cls, msg: Message) -> FormSettings:
        return cls(
            pokemon=msg.get_enum("pokemon", HoloPokemonId),
            forms=msg.get_object_list("forms", Form.from_message),
            ignore=msg.get_bool_or_false("moc_ignore"),
        )


@dataclass(frozen=True)
class Form:
    form: HoloPokemonForm
    is_costume: bool
    ignore: bool

    @classmethod
    def from_message(cls, msg: Message) -> Form:
        return cls(
            form=msg.get_enum("form", HoloPokemonForm),
            is_costume=msg.get_bool_or_false("isCostume"),
            ignore=msg.get_bool_or_false("moc_ignore"),
        )
