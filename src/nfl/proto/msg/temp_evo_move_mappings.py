from __future__ import annotations

from dataclasses import dataclass

from nfl.io import Message
from nfl.proto import HoloPokemonId, HoloPokemonMove, HoloTempEvoId


@dataclass(frozen=True)
class TempEvoMoveMappings:
    mappings: tuple[Mappings_TEMM, ...]

    @classmethod
    def from_message(cls, msg: Message) -> TempEvoMoveMappings:
        return cls(
            mappings=msg.get_object_list("mappings", Mappings_TEMM.from_message),
        )


@dataclass(frozen=True)
class Mappings_TEMM:
    pokemon_id: HoloPokemonId
    temp_evo_id: HoloTempEvoId
    move: HoloPokemonMove

    @classmethod
    def from_message(cls, msg: Message) -> Mappings_TEMM:
        return cls(
            pokemon_id=msg.get_enum("pokemon_id", HoloPokemonId),
            temp_evo_id=msg.get_enum_or_none("temp_evo_id", HoloTempEvoId),
            move=msg.get_enum("move", HoloPokemonMove),
        )
