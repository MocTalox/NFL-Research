from collections.abc import Callable, Iterable
from typing import Generic, TypeVar

from nfl.proto import HoloPokemonForm, HoloPokemonId

from .poke_species import PokeSpecies

T = TypeVar("T")


class PokeFormMap(Generic[T]):
    def __init__(
        self,
        items: Iterable[T],
        key1: Callable[[T], HoloPokemonId],
        key2: Callable[[T], HoloPokemonForm],
    ) -> None:
        self._data: dict[HoloPokemonId, dict[HoloPokemonForm, T]] = {}
        for item in items:
            self._data.setdefault(key1(item), {})[key2(item)] = item

    def get(self, poke: PokeSpecies) -> T | None:
        return self.get_poke_form(poke.name, poke.form)

    def get_poke_form(
        self,
        poke: HoloPokemonId,
        form: HoloPokemonForm | None = None,
    ) -> T | None:
        form = form if form is not None else HoloPokemonForm.FORM_UNSET
        inner = self._data.get(poke)
        return None if inner is None else inner.get(form)

    def __getitem__(self, key: HoloPokemonId):
        return self._data[key]

    def values(self) -> Iterable[Iterable[T]]:
        return (inner.values() for inner in self._data.values())
