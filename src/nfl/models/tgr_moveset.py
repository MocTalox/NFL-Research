from dataclasses import dataclass

from nfl.proto import (
    HoloAlignment,
    HoloPokemonForm,
    HoloPokemonId,
    HoloPokemonMove,
    HoloTempEvoId,
)


@dataclass(frozen=True)
class TgrPokemonInfo:
    id: HoloPokemonId
    form: HoloPokemonForm
    temp_evo: HoloTempEvoId
    alignment: HoloAlignment


@dataclass(frozen=True)
class TgrPokemonMoveset:
    pokemon: TgrPokemonInfo
    quick: HoloPokemonMove
    charge: HoloPokemonMove
    temp_evo_level: int = 0


@dataclass(frozen=True)
class TgrMovesetData:
    moveset: TgrPokemonMoveset
    damage_per_turn: float
    charge_damage: float
    charge_index: float
    charge_rate: float
    total_bulk: float
