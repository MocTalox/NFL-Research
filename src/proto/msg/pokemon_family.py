from __future__ import annotations
from dataclasses import dataclass
from core.gm_holoholo import HoloPokemonFamilyId
from proto.message import Message


@dataclass(frozen=True)
class PokemonFamily:
    family_id: HoloPokemonFamilyId
    
    @classmethod
    def from_message(cls, msg: Message) -> PokemonFamily:
        return cls(
            family_id=msg.get_enum("familyId", HoloPokemonFamilyId),
        )
