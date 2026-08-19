from __future__ import annotations

from dataclasses import dataclass

from nfl.io import Message
from nfl.proto import HoloPokemonMove, HoloPokemonType


@dataclass(frozen=True)
class BreadMoveMappings:
    mappings: tuple[Mappings_BMM, ...]

    @classmethod
    def from_message(cls, msg: Message) -> BreadMoveMappings:
        return cls(
            mappings=msg.get_object_list("mappings", Mappings_BMM.from_message),
        )


@dataclass(frozen=True)
class Mappings_BMM:
    type: HoloPokemonType
    move: HoloPokemonMove

    @classmethod
    def from_message(cls, msg: Message) -> Mappings_BMM:
        return cls(
            type=msg.get_enum("type", HoloPokemonType),
            move=msg.get_enum("move", HoloPokemonMove),
        )
