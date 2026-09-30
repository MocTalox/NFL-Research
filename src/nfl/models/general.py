from dataclasses import dataclass


@dataclass(frozen=True)
class PokemonStats:
    attack: float
    defense: float
    hp: int
    cp: int
