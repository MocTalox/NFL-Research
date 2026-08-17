from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar, NamedTuple

from nfl.proto import HoloPokemonId, HoloTempEvoId
from nfl.utils.poke_species import PokeSpecies
from nfl.utils.poke_map import PokeMap


P = TypeVar("P", bound=PokeSpecies)
F = TypeVar("F")


class PokeData(Generic[P]):

    def __init__(self):
        self._data: dict[PokeSpecies, P] = {}

    @classmethod
    def generate(cls, pokemons: Iterable[P]) -> PokeData[P]:
        result = cls()
        for pokemon in pokemons:
            if pokemon.identity in result._data:
                raise ValueError(f"Duplicate entry for identity: {pokemon.identity}")
            result._data[pokemon.identity] = pokemon
        return result

    def get(self, poke: PokeSpecies) -> P | None:
        return self._data.get(poke)

    def get_all_species(self) -> Iterable[PokeSpecies]:
        return self._data.keys()

    def get_all_pokes(self) -> Iterable[P]:
        return self._data.values()


def gen_pokemon_data(
    source: PokeMap[F],
    unfold: Callable[[F], list[P]]
) -> PokeData[P]:

    iterator_source = (inner.values() for inner in source.values())

    return gen_pokemon_data_raw(iterator_source, unfold)

def gen_pokemon_data_raw(
    source: Iterable[Iterable[F]],
    unfold: Callable[[F], Iterable[P]]
) -> PokeData[P]:

    all_pokemons = (
        (
            individual
            for form in pokemon
            for individual in unfold(form)
        )
        for pokemon in source
    )

    unique_pokemons = (
        pokemon
        for all_forms in all_pokemons
        for pokemon in normalize_forms(all_forms)
    )

    return PokeData[P].generate(unique_pokemons)

@dataclass
class PokeGroup(Generic[P]):
    main: P | None
    forms: list[P]

class GroupKey(NamedTuple):
    temp_evo: HoloTempEvoId
    shadow: bool

_NORMAL = {
    HoloPokemonId.CASTFORM,
    HoloPokemonId.DEOXYS,
    HoloPokemonId.ARCEUS,
    HoloPokemonId.GENESECT,
    HoloPokemonId.SILVALLY
}

def normalize_forms(
    species_stream: Iterable[P],
) -> Iterator[P]:
    poke_groups: dict[GroupKey, PokeGroup[P]] = defaultdict(lambda: PokeGroup(None, []))

    for poke in species_stream:
        poke_group = poke_groups[GroupKey(poke.temp_evo, poke.shadow)]
        poke_group.forms.append(poke)
        if not poke.form:
            assert poke_group.main is None
            poke_group.main = poke

    for poke_group in poke_groups.values():
        yield from collapse_forms(poke_group)

def collapse_forms(poke_group: PokeGroup[P]) -> Iterator[P]:
    main = poke_group.main
    forms = poke_group.forms
    assert main is not None

    if all(main.is_the_same(p) for p in forms):
        yield main
        return

    if not any(main.is_the_same(p) for p in forms if p is not main):
        yield from forms
        return

    normals = set(p.form for p in forms if p.form.name.endswith("_NORMAL"))
    if main.name not in _NORMAL and normals:
        yield from (p for p in forms if p.form not in normals)
        return

    # The `main` form is equivalent to another form.
    # For these species, the form is preferred over `main`.
    yield from (p for p in forms if p is not main)
