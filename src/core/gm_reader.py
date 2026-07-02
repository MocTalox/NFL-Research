import re

from functools import cache

from core.gm_constants import GAMEMASTER_LOCAL, OVERRIDES_LOCAL
from proto.message import Message
from utils.raw_value import RawValue


_OPENING_PATTERN = re.compile(r'([a-zA-Z0-9_]*) \{')
_ELEMENT_PATTERN = re.compile(r'([a-zA-Z0-9_]*): (?:"([^"]*)"|(.*))')
_CLOSING_PATTERN = re.compile(r'\}')


def _read_proto_file(filename: str) -> Message:
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()

    root = Message()
    stack = [root]

    for line in lines:
        token = _parse_line(line.strip())

        if token is None:
            continue

        match token:
            case ("opening", key):
                child = Message()
                current = stack[-1]
                current.add(key, child)
                stack.append(child)
            case ("element", key, value):
                current = stack[-1]
                current.add(key, value)
            case ("closing",):
                stack.pop()

    if len(stack) != 1:
        raise ValueError("Corrupted GM file")

    return root

def _parse_line(line: str):
    if match := _OPENING_PATTERN.fullmatch(line):
        return ("opening", match.group(1))

    if match := _ELEMENT_PATTERN.fullmatch(line):
        if match.group(2) is not None:
            return ("element", match.group(1), match.group(2))
        return ("element", match.group(1), RawValue(match.group(3)))

    if _CLOSING_PATTERN.fullmatch(line):
        return ("closing",)

    return None

@cache
def read_game_master() -> Message:
    return _read_proto_file(GAMEMASTER_LOCAL)

@cache
def read_overrides() -> Message:
    return _read_proto_file(OVERRIDES_LOCAL)
