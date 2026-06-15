from __future__ import annotations
from dataclasses import dataclass
from core.gm_holoholo import HoloPokemonId, HoloPokemonForm, HoloPokemonMove
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
    pokemon_id: HoloPokemonId
    form: HoloPokemonForm
    move: HoloPokemonMove

    @classmethod
    def from_message(cls, msg: Message) -> Mappings:
        return cls(
            pokemon_id=msg.get_enum("pokemonId", HoloPokemonId),
            form=msg.get_enum_or_none("form", HoloPokemonForm),
            move=msg.get_enum("move", HoloPokemonMove),
        )
