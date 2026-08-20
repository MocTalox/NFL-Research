from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Generic, NamedTuple, TypeVar

from nfl.proto import HoloAlignment, HoloBreadModeEnum, HoloPokemonId, HoloTempEvoId

from .poke_form_map import PokeFormMap
from .poke_species import PokeSpecies

P = TypeVar("P", bound=PokeSpecies)
F = TypeVar("F")


class PokeData(Generic[P]):
    def __init__(
        self,
        source: PokeFormMap[F] | Iterable[Iterable[F]],
        unfold: Callable[[F], Iterable[P]],
    ):
        if isinstance(source, PokeFormMap):
            source = source.values()

        all_pokemons = (
            (individual for form in pokemon for individual in unfold(form))
            for pokemon in source
        )

        unique_pokemons = (
            pokemon
            for all_forms in all_pokemons
            for pokemon in _normalize_forms(all_forms)
        )

        self._data: dict[PokeSpecies, P] = {}

        for pokemon in unique_pokemons:
            if pokemon.identity in self._data:
                raise ValueError(f"Duplicate entry for identity: {pokemon.identity}")
            self._data[pokemon.identity] = pokemon

    def get(self, poke: PokeSpecies) -> P | None:
        return self._data.get(poke)

    def get_all_species(self) -> Iterable[PokeSpecies]:
        return self._data.keys()

    def get_all_pokes(self) -> Iterable[P]:
        return self._data.values()


@dataclass
class _PokeGroup(Generic[P]):
    main: P | None
    forms: list[P]


class _GroupKey(NamedTuple):  # TODO maybe specified user-side
    temp_evo: HoloTempEvoId
    shadow: HoloAlignment
    bread: HoloBreadModeEnum


_NORMAL = {
    HoloPokemonId.CASTFORM,
    HoloPokemonId.DEOXYS,
    HoloPokemonId.ARCEUS,
    HoloPokemonId.GENESECT,
    HoloPokemonId.SILVALLY,
}


def _normalize_forms(
    species_stream: Iterable[P],
) -> Iterator[P]:
    poke_groups: dict[_GroupKey, _PokeGroup[P]] = defaultdict(
        lambda: _PokeGroup(None, [])
    )

    for poke in species_stream:
        poke_group = poke_groups[_GroupKey(poke.temp_evo, poke.shadow, poke.bread)]
        poke_group.forms.append(poke)
        if not poke.form:
            assert poke_group.main is None
            poke_group.main = poke

    for poke_group in poke_groups.values():
        yield from _collapse_forms(poke_group)


def _collapse_forms(poke_group: _PokeGroup[P]) -> Iterator[P]:
    main = poke_group.main
    forms = poke_group.forms
    assert main is not None

    if all(main.is_the_same(p) for p in forms):
        yield main
        return

    if not any(main.is_the_same(p) for p in forms if p is not main):
        yield from forms
        return

    normals = {p.form for p in forms if p.form.name.endswith("_NORMAL")}
    if main.name not in _NORMAL and normals:
        yield from (p for p in forms if p.form not in normals)
        return

    # The `main` form is equivalent to another form.
    # For these species, the form is preferred over `main`.
    yield from (p for p in forms if p is not main)
