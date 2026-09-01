from math import ceil, floor

from nfl.utils import f32


def bar_percent_raw(value: int, max_value: int) -> float:
    return f32(f32(value / max_value) * 100)


def bar_percent(value: int, max_value: int) -> int:
    return ceil(bar_percent_raw(value, max_value))


def bar_percent_old(value: int, max_value: int) -> int:
    return floor(bar_percent_raw(value, max_value))
