from collections.abc import Callable, Iterable
from typing import TypeAlias, TypeVar

from nfl.proto import HoloPokemonForm, HoloPokemonId

T = TypeVar("T")

PokeMap: TypeAlias = dict[HoloPokemonId, dict[HoloPokemonForm, T]]


def to_poke_map(
    items: Iterable[T],
    key1: Callable[[T], HoloPokemonId],
    key2: Callable[[T], HoloPokemonForm],
) -> PokeMap[T]:
    result: PokeMap[T] = {}

    for item in items:
        result.setdefault(key1(item), {})[key2(item)] = item

    return result


def get_poke(data: PokeMap[T], key1: HoloPokemonId, key2: HoloPokemonForm) -> T | None:
    inner = data.get(key1)
    return None if inner is None else inner.get(key2)
