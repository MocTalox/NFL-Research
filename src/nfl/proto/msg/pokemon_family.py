from __future__ import annotations

from dataclasses import dataclass

from nfl.proto import HoloPokemonFamilyId, Message


@dataclass(frozen=True)
class PokemonFamily:
    family_id: HoloPokemonFamilyId

    @classmethod
    def from_message(cls, msg: Message) -> PokemonFamily:
        return cls(
            family_id=msg.get_enum("familyId", HoloPokemonFamilyId),
        )
