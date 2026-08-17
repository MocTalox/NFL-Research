from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from functools import total_ordering
from operator import attrgetter

from nfl.proto import SizeSettings


@total_ordering
class SizeClass(Enum):
    XXS = (-2, attrgetter("xxs_lower_bound", "xs_lower_bound"))
    XS = (-1, attrgetter("xs_lower_bound", "m_lower_bound"))
    M = (0, attrgetter("m_lower_bound", "m_upper_bound"))
    XL = (1, attrgetter("m_upper_bound", "xl_upper_bound"))
    XXL = (2, attrgetter("xl_upper_bound", "xxl_upper_bound"))

    def __init__(self, id: int, bounds: Callable[[SizeSettings], tuple[float, float]]):
        self._ordinal = id
        self._bounds = bounds

    def __str__(self):
        return self.name

    def __lt__(self, other: SizeClass):
        return self._ordinal < other._ordinal

    def get_bounds(self, size_settings: SizeSettings):
        return self._bounds(size_settings)

    def in_bounds(self, height: float, size_settings: SizeSettings):
        height_min, height_max = self.get_bounds(size_settings)
        return (
            (self is SizeClass.XXS or height_min <= height)
            and
            (self is SizeClass.XXL or height <= height_max)
        )

    @classmethod
    def from_height(cls, height: float, size_settings: SizeSettings):
        return next(size for size in cls if size.in_bounds(height, size_settings))
