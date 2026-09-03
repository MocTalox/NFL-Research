import json
from dataclasses import asdict
from enum import Enum
from typing import Any

from nfl.calcs import (
    BattlePokemon,
    BattleState,
    calc_damage,
    get_cpm,
    get_rcpm,
    get_tgr_cp,
    get_tgr_hp,
    get_tgr_stats,
)
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
)
from nfl.proto import (
    HoloCharacterCategory,
    HoloCombatType,
    HoloPokemonForm,
    HoloPokemonId,
    HoloPokemonMove,
    HoloPokemonType,
    HoloWeatherCondition,
)


class EnumEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, Enum):
            return o.name
        return super().default(o)


def _dataclass_to_json(obj: Any) -> str:
    return json.dumps(asdict(obj), cls=EnumEncoder)


def _enum_name(enum: Enum) -> str:
    return enum.name.replace("_", " ").title()


def api_get_pokemon():
    return [_enum_name(pokemon) for pokemon in HoloPokemonId]


def api_get_forms(pokemon: str | None = None):
    if pokemon is not None:
        pokemon_species = PokeSpecies.resolve(name=pokemon)
        forms_src = [HoloPokemonForm.FORM_UNSET, *FORMS[pokemon_species.name]]
    else:
        forms_src = iter(HoloPokemonForm)

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

    return [_enum_name(move) for move in moves]


def api_get_characters():
    return [_enum_name(character) for character in HoloCharacterCategory]


def api_calculate_tgr_damage(
    payload: dict[str, Any],
) -> dict[str, Any]:
    pokemon_species = PokeSpecies.resolve(
        payload["pokemon"],
        payload.get("form"),
        payload.get("temp_evo"),
        payload.get("alignment"),
    )
    enemy_species = PokeSpecies.resolve(
        payload["enemy_pokemon"],
        payload.get("enemy_form"),
        payload.get("enemy_temp_evo"),
        "Shadow",  # TODO HoloAlignment.SHADOW ?
    )

    min_atk = payload["min_atk"]
    max_atk = payload["max_atk"]
    min_level = payload["min_level"]
    max_level = payload["max_level"]
    level = payload["trainer_level"]
    move = HoloPokemonMove[PokeSpecies.resolve_id(payload["move"])]
    enemy = HoloCharacterCategory[PokeSpecies.resolve_id(payload["enemy_character"])]

    a, d, _ = get_tgr_stats(enemy_species, level, enemy, 15, 15, 15)
    hp = get_tgr_hp(enemy_species, level, enemy, 15)
    cp = get_tgr_cp(enemy_species, level, enemy, 15, 15, 15)

    enemy_info: dict[str, Any] = {"atk": a, "def": d, "hp": hp, "cp": cp}

    m = PVP_MOVES[move]
    b = BattleState(HoloCombatType.VS_SEEKER)
    e = BattlePokemon(enemy_species, 15, 15, 15, get_rcpm(level), enemy)

    breakpoints: list[dict[str, Any]] = []
    for atk in range(min_atk, max_atk + 1):
        damages: list[dict[str, Any]] = []
        for level in range(min_level * 2, max_level * 2 + 1):
            level = level / 2
            p = BattlePokemon(pokemon_species, atk, 15, 15, get_cpm(level))
            dmg = calc_damage(p, e, m, False, False, b)
            damages.append({"level": level, "damage": dmg})
        breakpoints.append({"atk": atk, "damages": damages})

    return {"enemy": enemy_info, "breakpoints": breakpoints}


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
                type_effective.attack_scalar, list(HoloPokemonType)[1:]
            )
            if value != 1.0
        ],
    }
    return json.dumps(res)


def api_get_cpm(level: float):
    cpm = get_cpm(level)
    return json.dumps({"cpm": cpm})
