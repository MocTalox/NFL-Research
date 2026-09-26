from ._gm_data import (
    CachedGameMasterAccess,
    DefaultGameMasterAccess,
    FileGameMasterAccess,
    GameMasterAccess,
    RemoteGameMasterAccess,
)
from .message import Message
from .template import Template

_access: GameMasterAccess = DefaultGameMasterAccess()


def configure_game_master_access(access: GameMasterAccess) -> None:
    global _access
    _access = access


def get_templates_keys() -> set[str]:
    return _access.get_templates_keys()


def get_templates(key: str) -> dict[str, Template]:
    return _access.get_templates(key)


def get_experiments() -> list[int]:
    return _access.get_experiments()


def get_timestamp() -> int:
    return _access.get_timestamp()


__all__ = [
    "CachedGameMasterAccess",
    "DefaultGameMasterAccess",
    "FileGameMasterAccess",
    "GameMasterAccess",
    "Message",
    "RemoteGameMasterAccess",
    "Template",
    "configure_game_master_access",
    "get_experiments",
    "get_templates",
    "get_templates_keys",
    "get_timestamp",
]
