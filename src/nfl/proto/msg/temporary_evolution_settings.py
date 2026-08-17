from __future__ import annotations

from dataclasses import dataclass

from nfl.proto import HoloPokemonId, HoloTempEvoId, Message


@dataclass(frozen=True)
class TemporaryEvolutionSettings:
    pokemon_id: HoloPokemonId
    temporary_evolutions: tuple[TemporaryEvolutions, ...]

    @classmethod
    def from_message(cls, msg: Message) -> TemporaryEvolutionSettings:
        return cls(
            pokemon_id=msg.get_enum("pokemonId", HoloPokemonId),
            temporary_evolutions=msg.get_object_list(
                "temporary_evolutions", TemporaryEvolutions.from_message
            ),
        )


@dataclass(frozen=True)
class TemporaryEvolutions:
    temporary_evolution_id: HoloTempEvoId

    @classmethod
    def from_message(cls, msg: Message) -> TemporaryEvolutions:
        return cls(
            temporary_evolution_id=msg.get_enum("temporaryEvolutionId", HoloTempEvoId),
        )
