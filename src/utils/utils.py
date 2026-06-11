from typing import TypeAlias, TypeVar
from collections.abc import Iterable, Callable

import re
import struct

T = TypeVar("T")

DuoMap: TypeAlias = dict[str, dict[str | None, T]]


def f32(value: float | str) -> float:
    """
    Convert a Python float or decimal string to the nearest IEEE-754 float32.
    Returns the result as a Python float (still stored as float64,
    but with float32 precision).
    """
    return struct.unpack('>f', struct.pack('>f', float(value)))[0]

def f32_step(value: float | str, steps: int) -> float:
    """
    Move by a number of float32 representable values (ULPs).

    steps=1   -> next float32
    steps=-1  -> previous float32
    steps=10  -> jump forward 10 float32 values
    """
	# Float32 -> raw 32-bit integer bits.
    bits = struct.unpack('>I', struct.pack('>f', float(value)))[0]

    # For positive numbers, IEEE-754 bit ordering matches numeric ordering.
    # For negative numbers, reverse the direction.
    if bits & 0x80000000:
        bits -= steps
    else:
        bits += steps

	# Raw 32-bit integer bits -> float32.
    return struct.unpack('>f', struct.pack('>I', bits & 0xFFFFFFFF))[0]

def f32_diff(a: float | str, b: float | str) -> int:
    """
    Number of float32 representable values between a and b.

    Positive result: b > a
    Negative result: b < a
    """
    a_bits = struct.unpack('>I', struct.pack('>f', float(a)))[0]
    a_bits = ~a_bits & 0xFFFFFFFF if a_bits & 0x80000000 else a_bits | 0x80000000

    b_bits = struct.unpack('>I', struct.pack('>f', float(b)))[0]
    b_bits = ~b_bits & 0xFFFFFFFF if b_bits & 0x80000000 else b_bits | 0x80000000

    return b_bits - a_bits

def f32_str(value: float | str) -> str:
    bits = struct.unpack('>I', struct.pack('>f', float(value)))[0]

    for digits in range(1, 20):
        s = format(value, f'.{digits}g')
        s_bits = struct.unpack('>I', struct.pack('>f', float(s)))[0]
        if s_bits == bits:
            return s

    return str(value)

def f64(value: float | str) -> float:
    return float(f32_str(value))

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

def to_screaming_snake_case(text: str) -> str:
    # Convert camelCase/PascalCase boundaries to underscores
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)

    # Replace non-alphanumeric sequences with underscores
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)

    # Collapse multiple underscores
    text = re.sub(r"_+", "_", text)

    # Remove leading/trailing underscores and turn upper case
    return text.strip("_").upper()
