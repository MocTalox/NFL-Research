from math import ceil, floor
from nfl.utils.float32 import f32


def percent_raw(value: int, max_value: int) -> float:
    return f32(f32(value / max_value) * 100)

def percent(value: int, max_value: int) -> int:
    return ceil(percent_raw(value, max_value))

def percent_old(value: int, max_value: int) -> int:
    return floor(percent_raw(value, max_value))
