from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class BreadPokemonScalingSettings:
    visual_settings: tuple[VisualSettings, ...]

    @classmethod
    def from_message(cls, msg: Message) -> BreadPokemonScalingSettings:
        return cls(
            visual_settings=msg.get_object_list("visualSettings", VisualSettings.from_message),
        )

@dataclass(frozen=True)
class VisualSettings:
    pokemon_id: str
    pokemon_form_data: PokemonFormData

    @classmethod
    def from_message(cls, msg: Message) -> VisualSettings:
        return cls(
            pokemon_id=msg.get_string("pokemonId"),
            pokemon_form_data=msg.get_object("pokemonFormData", PokemonFormData.from_message),
        )

@dataclass(frozen=True)
class PokemonFormData:
    pokemon_form: str | None
    visual_data: tuple[VisualData, ...]

    @classmethod
    def from_message(cls, msg: Message) -> PokemonFormData:
        return cls(
            pokemon_form=msg.get_string_or_none("pokemonForm"),
            visual_data=msg.get_object_list("visualData", VisualData.from_message),
        )

@dataclass(frozen=True)
class VisualData:
    bread_mode: str

    @classmethod
    def from_message(cls, msg: Message) -> VisualData:
        return cls(
            bread_mode=msg.get_string("breadMode"),
        )
