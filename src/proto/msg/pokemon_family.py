from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class PokemonFamily:
    family_id: str
    
    @classmethod
    def from_message(cls, msg: Message) -> PokemonFamily:
        return cls(
            family_id=msg.get_string("familyId"),
        )
