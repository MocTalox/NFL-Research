from typing import Callable, TypeVar, Generic

T = TypeVar("T")


class CsvList(Generic[T]):
    def __init__(self) -> None:
        self._columns: list[Callable[[T | None], str]] = []
        self._rows: list[T | None] = [None]

    def __str__(self) -> str:
        return "\n".join([
            self._csv_row(row)
            for row in self._rows
        ])

    def add_row(self, row_object: T) -> None:
        self._rows.append(row_object)

    def add_colum(self, name: str, getter: Callable[[T], object]) -> None:
        self._columns.append(lambda row: str(getter(row)) if row else name)

    def _csv_row(self, row: T | None) -> str:
        return ",".join(
            CsvList._escape(column(row))
            for column in self._columns
        )

    @staticmethod
    def _escape(value: str) -> str:
        if any(c in value for c in (",", '"', "\n")):
            value = value.replace('"', '""')
            return f'"{value}"'
        return value
