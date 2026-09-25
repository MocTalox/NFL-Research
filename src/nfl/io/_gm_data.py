import pickle
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from typing import Any, Protocol
from urllib.request import urlopen

from nfl.exceptions import ConfigurationError
from nfl.utils._resources import read_resource_file_as_stream

from ._gm_builder import build_game_master
from .template import Template


class GameMasterAccess(Protocol):
    def get_game_master(
        self,
    ) -> tuple[dict[str, dict[str, Template]], list[int], int]: ...

    def get_templates(self, key: str) -> dict[str, Template]: ...

    def get_experiments(self) -> list[int]: ...

    def get_timestamp(self) -> int: ...


class DefaultGameMasterAccess:
    def _read_game_master(self) -> Iterator[str]:
        return read_resource_file_as_stream("gamemaster.txt")

    def _read_overrides(self) -> Iterator[str] | None:
        return read_resource_file_as_stream("overrides.txt")

    @cache  # noqa: B019 — instances are long-lived and few in number
    def get_game_master(self) -> tuple[dict[str, dict[str, Template]], list[int], int]:
        try:
            game_master_text = self._read_game_master()
            overrides_text = self._read_overrides()
            return build_game_master(game_master_text, overrides_text)

        except (ValueError, TypeError, KeyError) as e:
            raise ConfigurationError("INVALID_GAME_MASTER") from e

    def get_templates(self, key: str) -> dict[str, Template]:
        return self.get_game_master()[0][key]

    def get_experiments(self) -> list[int]:
        return self.get_game_master()[1]

    def get_timestamp(self) -> int:
        return self.get_game_master()[2]


class FileGameMasterAccess(DefaultGameMasterAccess):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read_game_master(self) -> Iterator[str]:
        with self.path.open("r", encoding="utf-8") as file:
            yield from file


class RemoteGameMasterAccess(DefaultGameMasterAccess):
    def __init__(self, url: str):
        self.url = url

    def _read_game_master(self) -> Iterator[str]:
        with urlopen(self.url) as response:
            for line in response:
                yield line.decode("utf-8")


class CachedGameMasterAccess:
    def __init__(self, path: str | Path, default: GameMasterAccess):
        self.path = Path(path)
        self.default = default

    def get_game_master(self) -> tuple[dict[str, dict[str, Template]], list[int], int]:
        return self.default.get_game_master()

    def get_templates(self, key: str) -> dict[str, Template]:
        elements = self._load_template_cache(key)

        if elements is not None:
            return elements

        elements = self.default.get_templates(key)
        self._save_template_cache(key, elements)

        return elements

    def get_experiments(self) -> list[int]:
        return self._get_metadata()[0]

    def get_timestamp(self) -> int:
        return self._get_metadata()[1]

    def _get_metadata(self):
        metadata = self._load_metadata_cache()

        if metadata is not None:
            return metadata

        metadata = self.default.get_experiments(), self.default.get_timestamp()
        self._save_metadata_cache(metadata)

        return metadata

    def _cache_file(self, key: str) -> Path:
        return self.path / f"{key}.pkl"

    def _load_template_cache(self, key: str):
        file = self._cache_file(key)

        if file.is_file():
            with file.open("rb") as f:
                return pickle.load(f)

    def _save_template_cache(self, key: str, data: Any):
        file = self._cache_file(key)
        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load_metadata_cache(self):
        file = self._cache_file("gm-metadata")

        if file.is_file():
            with file.open("rb") as f:
                return pickle.load(f)

    def _save_metadata_cache(self, data: Any):
        file = self._cache_file("gm-metadata")
        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
