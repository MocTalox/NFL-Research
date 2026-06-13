import re

from functools import cache

from core.gm_constants import GAMEMASTER_LOCAL, OVERRIDES_LOCAL
from proto.message import Message


_OPEN_PATTERN = re.compile(r"([a-zA-Z0-9_]*) \{")
_ELEM_PATTERN = re.compile(r"([a-zA-Z0-9_]*): (.*)")
_CLOSE_PATTERN = re.compile(r"\}")


def _read_proto_file(filename: str) -> Message:
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()

    root = Message()
    stack = [root]

    for line in lines:
        token = _parse_line(line.strip())

        if token is None:
            continue

        kind = token[0]

        if kind == "open":
            key = token[1]

            child = Message()

            current = stack[-1]
            current.add(key, child)

            stack.append(child)

        elif kind == "elem":
            key, value = token[1], token[2]

            current = stack[-1]
            current.add(key, value)

        elif kind == "close":
            stack.pop()

    if len(stack) != 1:
        raise ValueError("Corrupted GM file")

    return root

def _parse_line(line: str) -> tuple[str, ...] | None:
    if match := _OPEN_PATTERN.fullmatch(line):
        return ("open", match.group(1))

    if match := _ELEM_PATTERN.fullmatch(line):
        return ("elem", match.group(1), match.group(2))

    if _CLOSE_PATTERN.fullmatch(line):
        return ("close",)

    return None

@cache
def read_game_master() -> Message:
    return _read_proto_file(GAMEMASTER_LOCAL)

@cache
def read_overrides() -> Message:
    return _read_proto_file(OVERRIDES_LOCAL)
