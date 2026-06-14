from typing import TypeAlias, TypeVar
from collections.abc import Iterable, Callable


T = TypeVar("T")

DuoMap: TypeAlias = dict[str, dict[str | None, T]]


def to_duo_map(
    items: Iterable[T],
    key1: Callable[[T], str],
    key2: Callable[[T], str | None],
) -> DuoMap[T]:
    result: DuoMap[T] = {}

    for item in items:
        result.setdefault(key1(item), {})[key2(item)] = item

    return result

def duo_get(data: DuoMap[T], key1: str, key2: str | None) -> T | None:
    inner = data.get(key1)
    return None if inner is None else inner.get(key2)
