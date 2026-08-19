from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from typing import Literal, TypeAlias

from nfl.utils._resources import read_data_resource_files

"""
total = 23978
blocks = 2747
messages = 2017
enum = 677
oneof = 53
values = 18482
core = 1882
"""
_COMMENT_BLOCK_OPENING_PATTERN = re.compile(r"/\*")
_COMMENT_BLOCK_CLOSING_PATTERN = re.compile(r"\*/")
_COMMENT_LINE_PATTERN = re.compile(r"//.*")
_SYNTAX_PATTERN = re.compile(r'syntax\s*=\s*"proto3";')
_PACKAGE_PATTERN = re.compile(r"package\s+[\w\.]+;")
_ENUM_OPENING_PATTERN = re.compile(r"enum\s+(\w+)\s*\{")
_ENUM_ELEMENT_PATTERN = re.compile(r"(\w+)\s*=\s*(-?\d+);")
_ONEOF_OPENING_PATTERN = re.compile(r"oneof\s+(\w+)\s*\{")
_ONEOF_ELEMENT_PATTERN = re.compile(r"(\w+)\s+(\w+)\s*=\s*(\d+);")
_MESSAGE_OPENING_PATTERN = re.compile(r"message\s+(\w+)\s*\{")
_MESSAGE_ELEMENT_PATTERN = re.compile(
    r"(repeated\s+)?([\w\.]+|map<[\w\.]+,\s*[\w\.]+>)\s+(\w+)\s*=\s*(\d+);"
)
_CLOSING_PATTERN = re.compile(r"\}")

State: TypeAlias = Literal["init1", "init2", "comment", "message", "oneof", "enum"]

DataType: TypeAlias = Literal["core", "message", "oneof", "enum"]


@dataclass
class Data:
    data_type: DataType
    name: str
    childs: list[Data]
    values: list[Value]
    fields: list[Field]


@dataclass
class Value:
    key: str
    value: int


@dataclass
class Field:
    repeated: bool
    var_type: str
    key: str
    value: int


def _parse_proto_file(text: str) -> Data:
    total = 0
    blocks = 0
    messages = 0
    enum = 0
    oneof = 0
    values = 0

    lines = text.splitlines()

    root = Data("core", "", [], [], [])
    stack: list[tuple[Data, State]] = [(root, "init1")]

    for line in lines:
        data, state = stack[-1]
        token = _parse_line(line.strip(), state)

        if token is None:
            continue

        match token:
            case ("s",):
                total += 1
                stack.pop()
                stack.append((data, "init2"))
            case ("p",):
                total += 1
                stack.pop()
                stack.append((data, "message"))
            case ("cbo",):
                stack.append((data, "comment"))
            case ("cbc",):
                stack.pop()
            case ("eo", key):
                total += 1
                enum += 1
                child = Data("enum", key, [], [], [])
                data.childs.append(child)
                stack.append((child, "enum"))
            case ("ee", key, value):
                total += 1
                values += 1
                data.values.append(Value(key, value))
            case ("oo", key):
                total += 1
                oneof += 1
                child = Data("oneof", key, [], [], [])
                data.childs.append(child)
                stack.append((child, "oneof"))
            case ("oe", var, key, value):
                total += 1
                values += 1
                data.fields.append(Field(False, var, key, value))
            case ("mo", key):
                total += 1
                messages += 1
                child = Data("message", key, [], [], [])
                data.childs.append(child)
                stack.append((child, "message"))
            case ("me", rep, var, key, value):
                total += 1
                values += 1
                data.fields.append(Field(rep, var, key, value))
            case ("c",):
                total += 1
                blocks += 1
                stack.pop()

    if len(stack) != 1 or stack[0][1] != "message":
        raise ValueError("Corrupted Proto file")

    print(f"total = {total}")
    print(f"blocks = {blocks}")
    print(f"messages = {messages}")
    print(f"enum = {enum}")
    print(f"oneof = {oneof}")
    print(f"values = {values}")
    print(len(root.childs))
    print(len(root.values))
    print(len(root.fields))
    return root


def _parse_line(line: str, state: State):
    if not line or _COMMENT_LINE_PATTERN.fullmatch(line):
        return None

    if _COMMENT_BLOCK_OPENING_PATTERN.fullmatch(line):
        return ("cbo",)

    match state:
        case "init1":
            if _SYNTAX_PATTERN.fullmatch(line):
                return ("s",)
        case "init2":
            if _PACKAGE_PATTERN.fullmatch(line):
                return ("p",)
        case "message":
            if match := _MESSAGE_OPENING_PATTERN.fullmatch(line):
                return ("mo", match.group(1))
            if match := _ONEOF_OPENING_PATTERN.fullmatch(line):
                return ("oo", match.group(1))
            if match := _ENUM_OPENING_PATTERN.fullmatch(line):
                return ("eo", match.group(1))
            if match := _MESSAGE_ELEMENT_PATTERN.fullmatch(line):
                return (
                    "me",
                    bool(match.group(1)),
                    match.group(2),
                    match.group(3),
                    int(match.group(4)),
                )
            if _CLOSING_PATTERN.fullmatch(line):
                return ("c",)
        case "oneof":
            if match := _ONEOF_ELEMENT_PATTERN.fullmatch(line):
                return ("oe", match.group(1), match.group(2), int(match.group(3)))
            if _CLOSING_PATTERN.fullmatch(line):
                return ("c",)
        case "enum":
            if match := _ENUM_ELEMENT_PATTERN.fullmatch(line):
                return ("ee", match.group(1), int(match.group(2)))
            if _CLOSING_PATTERN.fullmatch(line):
                return ("c",)
        case "comment":
            if _COMMENT_BLOCK_CLOSING_PATTERN.fullmatch(line):
                return ("cbc",)

    if state == "comment":
        return None

    raise ValueError("Corrupted Proto file")


@cache
def read_proto_file() -> Data:
    text = read_data_resource_files("gamemaster.proto")
    return _parse_proto_file(text)
