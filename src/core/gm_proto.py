from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from proto.message import Message
from core.gm_holoholo import GAME_MASTER


class GMProto:
    def __init__(self, field_key: str | None):
        self._field_key = field_key
        self._fields: dict[str, GMProto] = {}
        self._times: dict[int, int] = defaultdict(int)

        self._total = 0
        self._bound = 0

    def field_key(self) -> str | None:
        return self._field_key

    def fields(self) -> Iterable[GMProto]:
        return self._fields.values()

    def field(self, key: str) -> GMProto | None:
        return self._fields.get(key)

    def times(self) -> set[int]:
        return set(self._times)

    # TODO maybe default to 0 and return int only (not None)
    def times_count(self, n: int) -> int | None:
        return self._times.get(n)

    def total_amount(self) -> int:
        return self._total

    def bound_amount(self) -> int:
        return self._bound

    def __str__(self) -> str:
        return self.__format("")

    def __format(self, prefix: str) -> str:
        key = "<root>" if self._field_key is None else prefix + self._field_key

        next_prefix = (
            prefix
            if self._field_key is None
            else key + "."
        )

        lines = [
            f"{key}: {self._total}/{self._bound} {dict(self._times)}"
        ]

        for field in self._fields.values():
            lines.append(field.__format(next_prefix))

        return "\n".join(lines)

    def _finish(self) -> None:
        self._total = sum(
            size * count
            for size, count in self._times.items()
        )

        self._bound = sum(self._times.values())

        for field in self._fields.values():
            field._finish()

    @classmethod
    def extract_proto(cls, key: str) -> GMProto:
        assert (templates := GAME_MASTER.get(key))
        messages = [template.value for template in templates.values()]

        proto = cls(None)
        proto._times[1] = len(messages)

        for msg in messages:
            proto._extract_message_proto(msg)

        proto._finish()
        return proto

    def _extract_message_proto(self, msg: Message) -> None:
        for key, values in msg.items():
            field = self._fields.setdefault(key, GMProto(key))

            field._times[len(values)] += 1

            for value in values:
                if isinstance(value, Message):
                    field._extract_message_proto(value)
