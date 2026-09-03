from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Generic, NamedTuple, TypeVar

from nfl.exceptions import ValidationError
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

        all_pokemon = (
            (individual for form in pokemon for individual in unfold(form))
            for pokemon in source
        )

        unique_pokemon = (
            pokemon
            for all_forms in all_pokemon
            for pokemon in _normalize_forms(all_forms)
        )

        self._data: dict[PokeSpecies, P] = {}

        for pokemon in unique_pokemon:
            if pokemon.identity in self._data:
                raise ValidationError(
                    f"Duplicate entry for identity: {pokemon.identity}"
                )
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
    alignment: HoloAlignment
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
        group_key = _GroupKey(poke.temp_evo, poke.alignment, poke.bread)
        poke_group = poke_groups[group_key]
        poke_group.forms.append(poke)

        if not poke.form:
            if poke_group.main is not None:
                raise ValidationError(
                    f"Multiple main species in group {group_key!r}: "
                    f"{poke_group.main!r} and {poke!r}"
                )
            poke_group.main = poke

    for poke_group in poke_groups.values():
        yield from _collapse_forms(poke_group)


def _collapse_forms(poke_group: _PokeGroup[P]) -> Iterator[P]:
    main = poke_group.main
    forms = poke_group.forms

    if main is None:
        raise ValidationError(
            f"Species group contains forms but no main species: {forms!r}"
        )

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
