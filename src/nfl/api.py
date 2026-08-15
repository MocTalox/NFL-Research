from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any
import json

from core.gm_holoholo import HoloPokemonId, HoloPokemonForm, HoloPokemonMove, HoloPokemonType, HoloWeatherCondition, HoloCharacterCategory
from utils.poke_species import PokeSpecies
import service.common.data as data
import service.logic.pokemon_stats as stats


class EnumEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, Enum):
            return o.name
        return super().default(o)

def _dataclass_to_json(obj: Any) -> str:
    return json.dumps(asdict(obj), cls=EnumEncoder)

@dataclass
class PokeInput:
    name: str
    form: str | None = None
    temp_evo: str | None = None
    shadow: bool = False

def _enum_name(enum: Enum) -> str:
    return enum.name.replace("_", " ").title()

def get_pokemon_names(query: str | None = None):
    return {"pokemons": [
        _enum_name(pokemon)
        for pokemon in HoloPokemonId
        if not query or query.lower() in pokemon.name.lower()
    ]}

def get_pokemon_forms(pokemon: str | None = None, query: str | None = None):
    if pokemon is not None:
        pokemon_species = PokeSpecies.resolve(name=pokemon)
        forms_src = [pokemon_species.form] + data.FORMS[pokemon_species.name]
    else:
        forms_src = HoloPokemonForm

    return {"forms": [
        _enum_name(form)
        for form in forms_src
        if not query or query.lower() in form.name.lower()
    ]}

def get_move_names(pokemon: PokeInput, query: str | None = None):
    pokemon_species = PokeSpecies.resolve(name=pokemon.name, form=pokemon.form, temp_evo=pokemon.temp_evo)
    pokemon_settings = data.get_pokemon_settings(pokemon_species)
    assert pokemon_settings

    moves = [
        *pokemon_settings.quick_moves,
        *pokemon_settings.elite_quick_move,
        *pokemon_settings.legacy_quick_moves,
        *pokemon_settings.cinematic_moves,
        *pokemon_settings.elite_cinematic_move,
        *pokemon_settings.non_tm_cinematic_moves,
        *pokemon_settings.legacy_cinematic_moves,
    ]

    return {"moves": [
        _enum_name(move) 
        for move in moves 
        if not query or query.lower() in move.name.lower()
    ]}

def get_enemy_names():
    return {"characters": [
        _enum_name(character)
        for character in HoloCharacterCategory
    ]}

def calculate_damage(pokemon: PokeInput, move: str, min_atk: int, max_atk: int, min_level: int, max_level: int, enemy: str, enemy_pokemon: PokeInput, trainer_level: int) -> dict[str, Any]:
    from core.gm_holoholo import HoloPokemonMove, HoloCharacterCategory, HoloCombatType
    from service.common.data import get_pokemon_settings, PVP_MOVES
    from service.logic.damage_formula import damage_formula_raw, Pokemon, BattleState
    from service.logic.pokemon_stats import get_tgr_stats, get_tgr_hp, get_tgr_cp, get_cpm, get_rcpm
    from utils.poke_species import PokeSpecies

    pokemon_species = PokeSpecies.resolve(name=pokemon.name, form=pokemon.form, temp_evo=pokemon.temp_evo)
    enemy_pokemon_species = PokeSpecies.resolve(name=enemy_pokemon.name, form=enemy_pokemon.form, temp_evo=enemy_pokemon.temp_evo)
    move = PokeSpecies.resolve_id(move)
    enemy = PokeSpecies.resolve_id(enemy)

    ps = get_pokemon_settings(pokemon_species)
    eps = get_pokemon_settings(enemy_pokemon_species)
    assert ps and eps

    e = Pokemon(eps, 15, 15, 15, get_rcpm(trainer_level), True, False, HoloCharacterCategory[enemy])
    a, d, _ = get_tgr_stats(eps, e.cpm, e.tgr_member, 15, 15, 15)
    hp = get_tgr_hp(eps, e.cpm, e.tgr_member, 15)
    cp = get_tgr_cp(eps, e.cpm, e.tgr_member, 15, 15, 15)

    enemy_info: dict[str, Any] = {"atk": a, "def": d, "hp": hp, "cp": cp}

    m = PVP_MOVES[HoloPokemonMove[move]]
    b = BattleState(HoloCombatType.VS_SEEKER)

    breakpoints: list[dict[str, Any]] = []
    for atk in range(min_atk, max_atk + 1):
        damages: list[dict[str, Any]] = []
        for level in range(min_level * 2, max_level * 2 + 1):
            level = level / 2
            cpm = get_cpm(level)
            p = Pokemon(ps, atk, 15, 15, cpm, pokemon.shadow, False)
            dmg = damage_formula_raw(p, e, m.power, m.type, 0, False, b)
            damages.append({"level": level, "damage": int(dmg) + 1, "damage_raw": dmg})
        breakpoints.append({"atk": atk, "damages": damages})

    return {"enemy": enemy_info, "breakpoints": breakpoints}

### Other Examples of APIs ###

def get_pokemon_settings(pokemon: PokeInput):
    poke = PokeSpecies.resolve(name=pokemon.name, form=pokemon.form, temp_evo=pokemon.temp_evo)
    pokemon_settings = data.get_pokemon_settings(poke)
    if pokemon_settings is None:
        return None
    if poke.temp_evo:
        pokemon_settings = data.get_temp_evo_pokemon_settings(pokemon_settings, poke.temp_evo)
    return _dataclass_to_json(pokemon_settings)

def get_size_settings(pokemon: PokeInput):
    poke = PokeSpecies.resolve(name=pokemon.name, form=pokemon.form, temp_evo=pokemon.temp_evo)
    pokemon_extended_settings = data.get_pokemon_extended_settings(poke)
    if pokemon_extended_settings is None:
        return None
    if poke.temp_evo:
        size_settings = data.get_temp_evo_size_settings(pokemon_extended_settings, poke.temp_evo)
    else:
        size_settings = pokemon_extended_settings.size_settings
    return _dataclass_to_json(size_settings)

def get_pve_move_settings(move: str):
    holo_move = HoloPokemonMove[move]
    move_settings = data.PVE_MOVES[holo_move]
    return _dataclass_to_json(move_settings)

def get_pvp_move_settings(move: str):
    holo_move = HoloPokemonMove[move]
    move_settings = data.PVP_MOVES[holo_move]
    return _dataclass_to_json(move_settings)

def get_type_boosting_weather(type: str):
    holo_type = HoloPokemonType[type]
    weather = data.TYPES_WEATHER[holo_type]
    return json.dumps({"weather": weather})

def get_move_boosting_weather(move: str):
    holo_move = HoloPokemonMove[move]
    weather = data.get_move_boosting_weather(holo_move)
    return json.dumps({"weather": weather})

def get_weather_affinities(weather: str):
    holo_weather = HoloWeatherCondition[weather]
    weather_affinities = data.WEATHER[holo_weather]
    return _dataclass_to_json(weather_affinities)

def get_type_effectiveness(type: str):
    holo_type = HoloPokemonType[type]
    type_effective = data.TYPES[holo_type]
    res: dict[str, Any] = {
        "attack_type": type_effective.attack_type,
        "effectiveness": [
            {
                "defense_type": defense_type,
                "attack_scalar": value
            }
            for value, defense_type in zip(
                type_effective.attack_scalar,
                list(HoloPokemonType)[1:]
            )
            if value != 1.0
        ]
    }
    return json.dumps(res)

def get_cpm(level: float):
    cpm = stats.get_cpm(level)
    return json.dumps({"cpm": cpm})
