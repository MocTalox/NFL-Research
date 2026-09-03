from __future__ import annotations

from nfl.data import (
    PokeSpecies,
    SizeClass,
    get_pokemon_settings,
    get_size_settings,
)
from nfl.exceptions import ValidationError
from nfl.proto import HoloPokemonId, PokemonSettings, SizeSettings

_ZORUA = PokeSpecies(name=HoloPokemonId.ZORUA)
_ZORUA_POKEMON_SETTINGS = get_pokemon_settings(_ZORUA)
_ZORUA_SIZE_SETTINGS = get_size_settings(_ZORUA)


def zorua_size(
    buddy_pokemon: PokeSpecies,
    wild_zorua_weight_kg: float,
    wild_zorua_height_m: float,
    wild_zorua_size_class: SizeClass,
    glitched_temp_evo: bool = False,
):
    return zorua_size_raw(
        get_pokemon_settings(buddy_pokemon),
        get_size_settings(buddy_pokemon, glitched_temp_evo),
        wild_zorua_weight_kg,
        wild_zorua_height_m,
        wild_zorua_size_class,
    )


def zorua_size_raw(
    buddy_pokemon_settings: PokemonSettings,
    buddy_size_settings: SizeSettings,
    wild_zorua_weight_kg: float,
    wild_zorua_height_m: float,
    wild_zorua_size_class: SizeClass,
):
    if wild_zorua_weight_kg < 0 or wild_zorua_height_m < 0:
        raise ValidationError(
            f"Invalid Zorua dimensions: weight_kg={wild_zorua_weight_kg}, "
            f"height_m={wild_zorua_height_m}. Values must be positive."
        )
    if not wild_zorua_size_class.in_bounds(wild_zorua_height_m, _ZORUA_SIZE_SETTINGS):
        lower, upper = wild_zorua_size_class.get_bounds(_ZORUA_SIZE_SETTINGS)
        raise ValidationError(
            f"Size class mismatch: Zorua with height {wild_zorua_height_m}m "
            f"cannot be {wild_zorua_size_class} ([{lower}, {upper}])"
        )

    power = 1 if wild_zorua_size_class == SizeClass.XXL else 2

    wild_buddy_height_variant = (
        wild_zorua_height_m / buddy_pokemon_settings.pokedex_height_m
    )
    avg_weight = (
        wild_buddy_height_variant**power * buddy_pokemon_settings.pokedex_weight_kg
    )
    weight_index = (
        wild_zorua_weight_kg - avg_weight
    ) / buddy_pokemon_settings.weight_std_dev

    buddy_size_class = SizeClass.from_height(wild_zorua_height_m, buddy_size_settings)
    power = 1 if buddy_size_class == SizeClass.XXL else 2

    zorua_height_variant = min(max(wild_buddy_height_variant, 0.49), 1.75)
    zorua_avg_weight = (
        zorua_height_variant**power * _ZORUA_POKEMON_SETTINGS.pokedex_weight_kg
    )

    zorua_weight = (
        zorua_avg_weight + weight_index * _ZORUA_POKEMON_SETTINGS.weight_std_dev
    )
    zorua_height = zorua_height_variant * _ZORUA_POKEMON_SETTINGS.pokedex_height_m

    if zorua_weight <= 0:
        zorua_weight = zorua_avg_weight

    # TODO Verify if it should be the same as `buddy_size_class`
    # Note: No, it is not the same on sus pokemon (+pumpkaboo, h-lilligant, h-avalugg, etc)
    zorua_size_class = SizeClass.from_height(wild_zorua_height_m, buddy_size_settings)

    return (zorua_weight, zorua_height, zorua_size_class)
