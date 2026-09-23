from dataclasses import dataclass
from enum import Enum
from typing import Any

from nfl.calcs import (
    get_cp,
    get_hp,
    get_stats,
    get_tgr_cp,
    get_tgr_hp,
    get_tgr_stats,
)
from nfl.data import (
    FORMS,
    TEMP_EVOS,
    TYPES,
    PokeSpecies,
    get_pokemon_settings,
    is_tgr_member,
)
from nfl.exceptions import ValidationError
from nfl.proto import (
    HoloAlignment,
    HoloCharacterCategory,
    HoloPokemonForm,
    HoloPokemonId,
    HoloPokemonType,
    HoloTempEvoId,
)


@dataclass
class PokemonStats:
    attack: float
    defense: float
    hp: int
    cp: int


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
        temp_evos = TEMP_EVOS.get(pokemon_species.name, [])
        temp_evos_src = [HoloTempEvoId.TEMP_EVOLUTION_UNSET, *temp_evos]
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


def get_pokemon_stats(
    pokemon: HoloPokemonId,
    form: HoloPokemonForm = HoloPokemonForm.FORM_UNSET,
    temp_evo: HoloTempEvoId = HoloTempEvoId.TEMP_EVOLUTION_UNSET,
    level: float = 50.0,
    iv_atk: int = 15,
    iv_def: int = 15,
    iv_sta: int = 15,
    character: HoloCharacterCategory = HoloCharacterCategory.UNSET,
):
    ps = PokeSpecies(name=pokemon, form=form, temp_evo=temp_evo)

    if is_tgr_member(character):
        if not float(level).is_integer():
            raise ValidationError("TGR members Pokémons cannot be of half levels.")
        level = int(level)

        a, d, _ = get_tgr_stats(ps, level, character, iv_atk, iv_def, iv_sta)
        hp = get_tgr_hp(ps, level, character, iv_sta)
        cp = get_tgr_cp(ps, level, character, iv_atk, iv_def, iv_sta)
    else:
        a, d, _ = get_stats(ps, level, iv_atk, iv_def, iv_sta)
        hp = get_hp(ps, level, iv_sta)
        cp = get_cp(ps, level, iv_atk, iv_def, iv_sta)

    return PokemonStats(a, d, hp, cp)


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
