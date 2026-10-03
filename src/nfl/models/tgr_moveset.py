from dataclasses import dataclass

from nfl.data import PokeSpecies
from nfl.proto import HoloPokemonMove


@dataclass(frozen=True)
class TgrPokemonMoveset:
    pokemon: PokeSpecies
    quick: HoloPokemonMove
    charge: HoloPokemonMove


@dataclass(frozen=True)
class TgrMovesetData:
    moveset: TgrPokemonMoveset
    damage_per_turn: float
    charge_damage: float
    charge_index: float
    charge_rate: float
    total_bulk: float
