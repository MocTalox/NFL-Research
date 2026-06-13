import re

from functools import cache

from core.gm_reader import read_game_master
from proto.template import Template


@cache
def game_master() -> dict[str, dict[str, Template]]:
    data: dict[str, dict[str, Template]] = {}
    
    for template in read_game_master().get_object_list("template", Template):
        data.setdefault(template.key, {})[template.template_id] = template

    return data

@cache
def dex_number() -> dict[str, str | None]:
    _DEX_NUMBER_PATTERN = re.compile(r"V([0-9]{4})")

    def _get_number(template: Template) -> str | None:
        match = _DEX_NUMBER_PATTERN.search(template.template_id)
        return match.group(1) if match else None

    return {
        template.value.get_string("pokemon"): _get_number(template)
        for template in game_master()["formSettings"].values()
    }

TYPES_ENUM = {
    'POKEMON_TYPE_NORMAL': 1,
    'POKEMON_TYPE_FIGHTING': 2,
    'POKEMON_TYPE_FLYING': 3,
    'POKEMON_TYPE_POISON': 4,
    'POKEMON_TYPE_GROUND': 5,
    'POKEMON_TYPE_ROCK': 6,
    'POKEMON_TYPE_BUG': 7,
    'POKEMON_TYPE_GHOST': 8,
    'POKEMON_TYPE_STEEL': 9,
    'POKEMON_TYPE_FIRE': 10,
    'POKEMON_TYPE_WATER': 11,
    'POKEMON_TYPE_GRASS': 12,
    'POKEMON_TYPE_ELECTRIC': 13,
    'POKEMON_TYPE_PSYCHIC': 14,
    'POKEMON_TYPE_ICE': 15,
    'POKEMON_TYPE_DRAGON': 16,
    'POKEMON_TYPE_DARK': 17,
    'POKEMON_TYPE_FAIRY': 18
}
