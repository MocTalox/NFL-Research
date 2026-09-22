from enum import Enum
from typing import Any

from nfl.data import (
    FORMS,
    TEMP_EVOS,
    TYPES,
    PokeSpecies,
    get_pokemon_settings,
    is_tgr_member,
)
from nfl.proto import (
    HoloAlignment,
    HoloCharacterCategory,
    HoloPokemonForm,
    HoloPokemonId,
    HoloPokemonType,
    HoloTempEvoId,
)


def _enum_name(enum: Enum) -> str:
    return enum.name.replace("_", " ").title()


def get_pokemon():
    return [_enum_name(pokemon) for pokemon in HoloPokemonId if pokemon > 0]


def get_forms(pokemon: str | None = None):
    if pokemon is not None:
        pokemon_species = PokeSpecies.resolve(name=pokemon)
        forms_src = [HoloPokemonForm.FORM_UNSET, *FORMS[pokemon_species.name]]
    else:
        forms_src = (form for form in HoloPokemonForm if form > 0)

    return [_enum_name(form) for form in forms_src]


# TODO somehow TEMP_EVOS does not take into account forms
# So need to find another way to not give temp evos on armored mewtwo, galarian slowbro, etc.
def get_temp_evos(pokemon: str | None = None, form: str | None = None):
    if pokemon is not None:
        pokemon_species = PokeSpecies.resolve(name=pokemon)
        temp_evos_src = [
            HoloTempEvoId.TEMP_EVOLUTION_UNSET,
            *TEMP_EVOS[pokemon_species.name],
        ]
    else:
        temp_evos_src = (temp_evo for temp_evo in HoloTempEvoId if temp_evo > 0)

    return [_enum_name(temp_evo) for temp_evo in temp_evos_src]


def get_pokemon_moves(
    pokemon: str,
    form: str | None = None,
    temp_evo: str | None = None,
    alignment: str | None = None,
):
    pokemon_species = PokeSpecies.resolve(pokemon, form, temp_evo, alignment)
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

    if pokemon_settings.shadow is not None:
        if pokemon_species.alignment == HoloAlignment.SHADOW:
            moves.append(pokemon_settings.shadow.shadow_charge_move)
        if pokemon_species.alignment == HoloAlignment.PURIFIED:
            moves.append(pokemon_settings.shadow.purified_charge_move)

    if pokemon_settings.nfl_special_move:
        moves.append(pokemon_settings.nfl_special_move)

    return [_enum_name(move) for move in moves]


def get_alignments(include_unset: bool = True):
    min_value = 0 if include_unset else 1

    return [
        _enum_name(alignment) for alignment in HoloAlignment if alignment >= min_value
    ]


def get_characters(include_unset: bool = False, only_tgr: bool = False):
    min_value = 0 if include_unset else 1

    return [
        _enum_name(character)
        for character in HoloCharacterCategory
        if character >= min_value and (not only_tgr or is_tgr_member(character))
    ]


### Other Examples of APIs ###


def get_type_effectiveness(type: str) -> dict[str, Any]:
    type_effective = TYPES[HoloPokemonType[type]]

    return {
        "attack_type": type_effective.attack_type,
        "effectiveness": [
            {"defense_type": defense_type, "attack_scalar": value}
            for value, defense_type in zip(
                type_effective.attack_scalar,
                [t for t in HoloPokemonType if t > 0],
            )
            if value != 1.0
        ],
    }
