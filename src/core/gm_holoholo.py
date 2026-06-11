import re

from core.gm_reader import game_master
from proto.template import Template


GAME_MASTER: dict[str, dict[str, Template]] = {}

for template in game_master().get_object_list("template", Template):
    GAME_MASTER.setdefault(template.key, {})[template.template_id] = template

def _get_number(template: Template) -> str | None:
    match = re.compile(r"V([0-9]{4})").search(template.template_id)
    return match.group(1) if match else None

DEX_NUMBER: dict[str, str | None] = {}

DEX_NUMBER.update({
    template.value.get_string("pokemon"): _get_number(template)
    for template in GAME_MASTER["formSettings"].values()
})

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
