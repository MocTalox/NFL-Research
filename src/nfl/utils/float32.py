import struct


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

def has_decimals(value: float, decimals: int) -> bool:
    # from math import isclose
    # return isclose(round(height_m, 2), height_m)
    return round(value, decimals) == value
