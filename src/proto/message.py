from __future__ import annotations

from enum import IntEnum
from typing import Callable, Iterable, Literal, TypeVar, cast, overload

from utils.float32 import f32
from utils.raw_value import RawValue


T = TypeVar("T")
E = TypeVar("E", bound=IntEnum)


class Message:
    def __init__(self) -> None:
        self._data: dict[str, list[str | RawValue | Message]] = {}

    def __str__(self) -> str:
        return self.format_message()

    def format_message(self, indent: str = "") -> str:
        next_indent = indent + "  "
        lines = ["{"]

        for key, values in self.items():
            for value in values:
                value_str = (
                    f" {value.format_message(next_indent)}"
                    if isinstance(value, Message)
                    else f": {value}"
                )
                lines.append(f"{next_indent}{key}{value_str}")

        lines.append(indent + "}")
        return "\n".join(lines)

    def add(self, key: str, value: str | RawValue | Message) -> None:
        self._data.setdefault(key, []).append(value)

    def delete(self, key: str) -> None:
        del self._data[key]

    def get(self, key: str) -> list[str | RawValue | Message]:
        return self._data[key]

    def has(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> Iterable[str]:
        return self._data.keys()

    def items(self) -> Iterable[tuple[str, list[str | RawValue | Message]]]:
        return self._data.items()

    def get_message(self, key: str) -> Message:
        return self._get_single_element(key, Message)

    def get_message_or_none(self, key: str) -> Message | None:
        return self._get_single_element(key, Message, nullable=True)

    def get_object(self, key: str, mapper: Callable[[Message], T]) -> T:
        return mapper(self.get_message(key))

    def get_object_or_none(self, key: str, mapper: Callable[[Message], T]) -> T | None:
        msg = self.get_message_or_none(key)
        return None if msg is None else mapper(msg)

    def get_string(self, key: str) -> str:
        return self._get_single_element(key, str)

    def get_string_or_none(self, key: str) -> str | None:
        return self._get_single_element(key, str, nullable=True)

    def get_enum(self, key: str, enum_class: type[E]) -> E:
        return Message._to_enum(self._get_single_element(key, RawValue), enum_class)

    def get_enum_or_none(self, key: str, enum_class: type[E]) -> E:
        return Message._to_enum(self._get_single_element(key, RawValue, nullable=True), enum_class)

    def get_int(self, key: str) -> int:
        return int(self._get_single_element(key, RawValue).str_value)

    def get_int_or_zero(self, key: str) -> int:
        value = self._get_single_element(key, RawValue, nullable=True)
        return 0 if value is None else int(value.str_value)

    def get_float(self, key: str) -> float:
        return f32(self._get_single_element(key, RawValue).str_value)

    def get_float_or_zero(self, key: str) -> float:
        value = self._get_single_element(key, RawValue, nullable=True)
        return 0.0 if value is None else f32(value.str_value)

    def get_bool(self, key: str) -> bool:
        return self._get_single_element(key, RawValue).str_value.lower() == "true"

    def get_bool_or_false(self, key: str) -> bool:
        value = self._get_single_element(key, RawValue, nullable=True)
        return value is not None and value.str_value.lower() == "true"

    def get_message_list(self, key: str) -> tuple[Message, ...]:
        return tuple(self._get_many_elements(key, Message))

    def get_object_list(
        self,
        key: str,
        mapper: Callable[[Message], T],
        cond: str | Callable[[Message], bool] | None = None,
    ) -> tuple[T, ...]:
        if not cond:
            cond = lambda _: True
        if isinstance(cond, str):
            filter_key = cond
            cond = lambda m: m.has(filter_key)
        return tuple(mapper(msg) for msg in self._get_many_elements(key, Message) if cond(msg))

    def get_string_list(self, key: str) -> tuple[str, ...]:
        return tuple(self._get_many_elements(key, str))

    def get_enum_list(self, key: str, enum_class: type[E]) -> tuple[E, ...]:
        return tuple(Message._to_enum(id, enum_class) for id in self._get_many_elements(key, RawValue))

    def get_int_list(self, key: str) -> tuple[int, ...]:
        return tuple(int(v.str_value) for v in self._get_many_elements(key, RawValue))

    def get_float_list(self, key: str) -> tuple[float, ...]:
        return tuple(f32(v.str_value) for v in self._get_many_elements(key, RawValue))

    @overload
    def _get_single_element(self, key: str, expected_type: type[T]) -> T: ...

    @overload
    def _get_single_element(self, key: str, expected_type: type[T], nullable: Literal[False]) -> T: ...

    @overload
    def _get_single_element(self, key: str, expected_type: type[T], nullable: Literal[True]) -> T | None: ...

    def _get_single_element(
        self,
        key: str,
        expected_type: type[T],
        nullable: bool = False,
    ) -> T | None:
        values = self._data.get(key)

        if not values:
            if nullable:
                return None
            raise KeyError(f"Message does not contain key '{key}'")

        if len(values) > 1:
            raise ValueError(f"Multiple values found for key '{key}'")

        value = values[0]

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Expected {expected_type.__name__} for key '{key}', "
                f"got {type(value).__name__}"
            )

        return value

    def _get_many_elements(
        self,
        key: str,
        expected_type: type[T],
    ) -> list[T]:
        values = self._data.get(key) or []

        for value in values:
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Expected {expected_type.__name__} for key '{key}', "
                    f"got {type(value).__name__}"
                )

        return cast(list[T], values)

    @staticmethod
    def _to_enum(id: RawValue | None, enum_class: type[E]) -> E:
        if not id: # Default enum value if None
            return enum_class(0)
        try: # Try by name first
            return enum_class[id.str_value]
        except KeyError: # Otherwise try by numeric id
            return enum_class(int(id.str_value))
