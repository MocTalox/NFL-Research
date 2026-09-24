from dataclasses import dataclass
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


def get_pokemon_types(include_none: bool = True):
    min_value = 0 if include_none else 1

    return [poke_type for poke_type in HoloPokemonType if poke_type >= min_value]


def get_pokemon():
    return [pokemon for pokemon in HoloPokemonId if pokemon > 0]


def get_forms(pokemon: PokeSpecies | HoloPokemonId | None = None):
    if pokemon is not None:
        if isinstance(pokemon, PokeSpecies):
            pokemon = pokemon.name
        forms_src = [HoloPokemonForm.FORM_UNSET, *FORMS[pokemon]]
    else:
        forms_src = [form for form in HoloPokemonForm if form > 0]

    return forms_src


# TODO somehow TEMP_EVOS does not take into account forms
# So need to find another way to not give temp evos on armored mewtwo, galarian slowbro, etc.
def get_temp_evos(pokemon: PokeSpecies | None = None):
    if pokemon is not None:
        temp_evos = TEMP_EVOS.get(pokemon.name, [])
        temp_evos_src = [HoloTempEvoId.TEMP_EVOLUTION_UNSET, *temp_evos]
    else:
        temp_evos_src = [temp_evo for temp_evo in HoloTempEvoId if temp_evo > 0]

    return temp_evos_src


def get_pokemon_moves(pokemon: PokeSpecies):
    pokemon_settings = get_pokemon_settings(pokemon)

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
        if pokemon.alignment == HoloAlignment.SHADOW:
            moves.append(pokemon_settings.shadow.shadow_charge_move)
        if pokemon.alignment == HoloAlignment.PURIFIED:
            moves.append(pokemon_settings.shadow.purified_charge_move)

    if pokemon_settings.nfl_special_move:
        moves.append(pokemon_settings.nfl_special_move)

    return moves


def get_alignments(include_unset: bool = True):
    min_value = 0 if include_unset else 1

    return [alignment for alignment in HoloAlignment if alignment >= min_value]


def get_characters(include_unset: bool = False, only_tgr: bool = False):
    min_value = 0 if include_unset else 1

    return [
        character
        for character in HoloCharacterCategory
        if character >= min_value
        and (not only_tgr or is_tgr_member(character) or character == 0)
    ]


def get_pokemon_stats(
    pokemon: PokeSpecies,
    level: float = 50.0,
    iv_atk: int = 15,
    iv_def: int = 15,
    iv_sta: int = 15,
    character: HoloCharacterCategory = HoloCharacterCategory.UNSET,
):
    if is_tgr_member(character):
        if not float(level).is_integer():
            raise ValidationError("TGR members Pokémons cannot be of half levels.")
        level = int(level)

        a, d, _ = get_tgr_stats(pokemon, level, character, iv_atk, iv_def, iv_sta)
        hp = get_tgr_hp(pokemon, level, character, iv_sta)
        cp = get_tgr_cp(pokemon, level, character, iv_atk, iv_def, iv_sta)
    else:
        a, d, _ = get_stats(pokemon, level, iv_atk, iv_def, iv_sta)
        hp = get_hp(pokemon, level, iv_sta)
        cp = get_cp(pokemon, level, iv_atk, iv_def, iv_sta)

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
