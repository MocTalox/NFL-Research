from importlib.metadata import version

from nfl.data.poke_species import PokeSpecies

__version__ = version("nfl-research")
__all__ = [
    "PokeSpecies",
]
