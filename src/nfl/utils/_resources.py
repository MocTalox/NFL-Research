from collections.abc import Iterator
from importlib.resources import files


def read_resource_file(file: str) -> str:
    resource = files("nfl.io") / "files" / file
    return resource.read_text(encoding="utf-8")


def read_resource_file_as_stream(file: str) -> Iterator[str]:
    resource = files("nfl.io") / "files" / file

    with resource.open("r", encoding="utf-8") as f:
        yield from f
