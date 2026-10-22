from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def group_by(
    items: Iterable[T],
    key_getter: Callable[[T], K],
    value_getter: Callable[[T], V] = lambda t: t,
) -> dict[K, set[V]]:
    grouped: dict[K, set[V]] = defaultdict(set)

    for item in items:
        grouped[key_getter(item)].add(value_getter(item))

    return dict(grouped)
