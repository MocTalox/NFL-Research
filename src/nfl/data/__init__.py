from typing import Iterable

from nfl.proto.template import Template

from ._gm_data import GameMasterAccess, DefaultGameMasterAccess


_access: GameMasterAccess = DefaultGameMasterAccess()


def configure_game_master_access(access: GameMasterAccess) -> None:
    global _access
    _access = access

def get_game_master() -> dict[str, dict[str, Template]]:
    return _access.get_game_master()

def get_templates(key: str) -> dict[str, Template]:
    return _access.get_templates(key)
