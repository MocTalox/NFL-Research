import json
from dataclasses import asdict
from enum import Enum
from typing import Any

from nfl.calcs import get_cpm
from nfl.data import (
    FORMS,
    PVE_MOVES,
    PVP_MOVES,
    TYPES,
    TYPES_WEATHER,
    WEATHER,
    PokeSpecies,
    get_move_boosting_weather,
    get_pokemon_settings,
    get_size_settings,
    is_tgr_member,
)
from nfl.io import get_timestamp
from nfl.proto import (
    HoloCharacterCategory,
    HoloPokemonForm,
    HoloPokemonId,
    HoloPokemonMove,
    HoloPokemonType,
    HoloWeatherCondition,
)


class _EnumEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, Enum):
            return o.name
        return super().default(o)


def _dataclass_to_json(obj: Any) -> str:
    return json.dumps(asdict(obj), cls=_EnumEncoder)


def _enum_name(enum: Enum) -> str:
    return enum.name.replace("_", " ").title()


def api_get_gm_timestamp():
    return get_timestamp()


def api_get_pokemon():
    return [_enum_name(pokemon) for pokemon in HoloPokemonId if pokemon > 0]


def api_get_forms(pokemon: str | None = None):
    if pokemon is not None:
        pokemon_species = PokeSpecies.resolve(name=pokemon)
        forms_src = [HoloPokemonForm.FORM_UNSET, *FORMS[pokemon_species.name]]
    else:
        forms_src = (form for form in HoloPokemonForm if form > 0)

    return [_enum_name(form) for form in forms_src]


def api_get_pokemon_moves(
    pokemon: str, form: str | None = None, temp_evo: str | None = None
):
    pokemon_species = PokeSpecies.resolve(pokemon, form, temp_evo)
    pokemon_settings = get_pokemon_settings(pokemon_species)

    moves = [
        *pokemon_settings.quick_moves,
        *pokemon_settings.elite_quick_move,
        *pokemon_settings.legacy_quick_moves,
        *pokemon_settings.cinematic_moves,
        *pokemon_settings.elite_cinematic_move,
        *pokemon_settings.non_tm_cinematic_moves,
        *pokemon_settings.legacy_cinematic_moves,
    ]

    if pokemon_settings.nfl_special_move:
        moves.append(pokemon_settings.nfl_special_move)

    return [_enum_name(move) for move in moves]


def api_get_characters(include_unset: bool = False, only_tgr: bool = False):
    min_value = 0 if include_unset else 1

    return [
        _enum_name(character)
        for character in HoloCharacterCategory
        if character >= min_value and (not only_tgr or is_tgr_member(character))
    ]


### Other Examples of APIs ###


def api_get_pokemon_settings(
    pokemon: str, form: str | None = None, temp_evo: str | None = None
):
    pokemon_species = PokeSpecies.resolve(pokemon, form, temp_evo)
    pokemon_settings = get_pokemon_settings(pokemon_species)
    return _dataclass_to_json(pokemon_settings)


def api_get_size_settings(
    pokemon: str, form: str | None = None, temp_evo: str | None = None
):
    pokemon_species = PokeSpecies.resolve(pokemon, form, temp_evo)
    size_settings = get_size_settings(pokemon_species)
    return _dataclass_to_json(size_settings)


def api_get_pve_move_settings(move: str):
    holo_move = HoloPokemonMove[move]
    move_settings = PVE_MOVES[holo_move]
    return _dataclass_to_json(move_settings)


def api_get_pvp_move_settings(move: str):
    holo_move = HoloPokemonMove[move]
    move_settings = PVP_MOVES[holo_move]
    return _dataclass_to_json(move_settings)


def api_get_type_boosting_weather(type: str):
    holo_type = HoloPokemonType[type]
    weather = TYPES_WEATHER[holo_type]
    return json.dumps({"weather": weather})


def api_get_move_boosting_weather(move: str):
    holo_move = HoloPokemonMove[move]
    weather = get_move_boosting_weather(holo_move)
    return json.dumps({"weather": weather})


def api_get_weather_affinities(weather: str):
    holo_weather = HoloWeatherCondition[weather]
    weather_affinities = WEATHER[holo_weather]
    return _dataclass_to_json(weather_affinities)


def api_get_type_effectiveness(type: str):
    holo_type = HoloPokemonType[type]
    type_effective = TYPES[holo_type]
    res: dict[str, Any] = {
        "attack_type": type_effective.attack_type,
        "effectiveness": [
            {"defense_type": defense_type, "attack_scalar": value}
            for value, defense_type in zip(
                type_effective.attack_scalar, [t for t in HoloPokemonType if t > 0]
            )
            if value != 1.0
        ],
    }
    return json.dumps(res)


def api_get_cpm(level: float):
    cpm = get_cpm(level)
    return json.dumps({"cpm": cpm})
