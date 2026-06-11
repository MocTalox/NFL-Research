from __future__ import annotations

from typing import Callable, Iterable, Literal, TypeVar, cast, overload

from utils.utils import f32

T = TypeVar("T")


class Message:
    def __init__(self) -> None:
        self._data: dict[str, list[str | Message]] = {}

    def __str__(self) -> str:
        return self.format_message()

    def format_message(self, indent: str = "") -> str:
        next_indent = indent + "  "
        lines = ["{"]

        for key, values in self._data.items():
            for value in values:
                value_str = (
                    value.format_message(next_indent)
                    if isinstance(value, Message)
                    else str(value)
                )
                lines.append(f"{next_indent}{key}: {value_str}")

        lines.append(indent + "}")
        return "\n".join(lines)

    def add(self, key: str, value: str | Message) -> None:
        self._data.setdefault(key, []).append(value)

    def has(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> Iterable[str]:
        return self._data.keys()

    def items(self) -> Iterable[tuple[str, list[str | Message]]]:
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

    def get_int(self, key: str) -> int:
        return int(self.get_string(key))

    def get_int_or_zero(self, key: str) -> int:
        value = self.get_string_or_none(key)
        return 0 if value is None else int(value)

    def get_float(self, key: str) -> float:
        return f32(self.get_string(key))

    def get_float_or_zero(self, key: str) -> float:
        value = self.get_string_or_none(key)
        return 0.0 if value is None else f32(value)

    def get_bool(self, key: str) -> bool:
        return self.get_string(key).lower() == "true"

    def get_bool_or_false(self, key: str) -> bool:
        value = self.get_string_or_none(key)
        return value is not None and value.lower() == "true"

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
        return tuple(map(mapper, filter(cond, self._get_many_elements(key, Message))))

    def get_string_list(self, key: str) -> tuple[str, ...]:
        return tuple(self._get_many_elements(key, str))

    def get_int_list(self, key: str) -> tuple[int, ...]:
        return tuple(map(int, self._get_many_elements(key, str)))

    def get_float_list(self, key: str) -> tuple[float, ...]:
        return tuple(map(f32, self._get_many_elements(key, str)))

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
