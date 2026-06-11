from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class SourdoughMoveMappingSettings:
    mappings: tuple[Mappings, ...]

    @classmethod
    def from_message(cls, msg: Message) -> SourdoughMoveMappingSettings:
        return cls(
            mappings=msg.get_object_list("mappings", Mappings.from_message),
        )

@dataclass(frozen=True)
class Mappings:
    pokemon_id: str
    form: str | None
    move: str

    @classmethod
    def from_message(cls, msg: Message) -> Mappings:
        return cls(
            pokemon_id=msg.get_string("pokemonId"),
            form=msg.get_string_or_none("form"),
            move=msg.get_string("move"),
        )
