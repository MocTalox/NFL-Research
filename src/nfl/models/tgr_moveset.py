from dataclasses import dataclass

from nfl.data import PokeSpecies
from nfl.proto import HoloPokemonMove


@dataclass(frozen=True)
class TgrPokemonMoveset:
    pokemon: PokeSpecies
    quick: HoloPokemonMove
    charged: HoloPokemonMove


@dataclass(frozen=True)
class TgrMovesetData:
    moveset: TgrPokemonMoveset
    damage_per_turn: float
    charged_damage: float
    charged_index: float
    charged_rate: float
    total_bulk: float
