import pickle
from functools import cache
from pathlib import Path
from typing import Any, Protocol
from urllib.request import urlopen

from nfl.proto.template import Template
from nfl.utils._resources import read_data_resource_files

from ._gm_builder import build_game_master


class GameMasterAccess(Protocol):
    def get_game_master(self) -> dict[str, dict[str, Template]]: ...

    def get_templates(self, key: str) -> dict[str, Template]: ...


class DefaultGameMasterAccess:
    def _read_game_master(self) -> str:
        return read_data_resource_files("gamemaster.txt")

    def _read_overrides(self) -> str | None:
        return read_data_resource_files("overrides.txt")

    @cache  # noqa: B019 — instances are long-lived and few in number
    def get_game_master(self) -> dict[str, dict[str, Template]]:
        game_master_text = self._read_game_master()
        overrides_text = self._read_overrides()
        return build_game_master(game_master_text, overrides_text)

    def get_templates(self, key: str) -> dict[str, Template]:
        return self.get_game_master()[key]


class FileGameMasterAccess(DefaultGameMasterAccess):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read_game_master(self) -> str:
        return self.path.read_text(encoding="utf-8")


class RemoteGameMasterAccess(DefaultGameMasterAccess):
    def __init__(self, url: str):
        self.url = url

    def _read_game_master(self) -> str:
        with urlopen(self.url) as response:
            return response.read().decode("utf-8")


class CachedGameMasterAccess:
    def __init__(self, path: str | Path, default: GameMasterAccess):
        self.path = Path(path)
        self.default = default

    def get_game_master(self) -> dict[str, dict[str, Template]]:
        return self.default.get_game_master()

    def get_templates(self, key: str) -> dict[str, Template]:
        elements = self._load_cache(key)
        if elements is not None:
            return elements
        elements = self.default.get_templates(key)
        self._save_cache(key, elements)
        return elements

    def _cache_file(self, key: str) -> Path:
        return self.path / f"{key}.pkl"

    def _load_cache(self, key: str):
        file = self._cache_file(key)
        if file.is_file():
            with file.open("rb") as f:
                return pickle.load(f)

    def _save_cache(self, key: str, data: Any):
        file = self._cache_file(key)
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
