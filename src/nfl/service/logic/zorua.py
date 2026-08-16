from __future__ import annotations

from nfl.core.gm_holoholo import HoloPokemonId, HoloPokemonForm
from nfl.proto.msg.pokemon_settings import PokemonSettings
from nfl.proto.msg.pokemon_extended_settings import SizeSettings
from nfl.service.common.data import POKEMON, EXTENDED
from nfl.service.common.size_class import SizeClass


ZORUA_POKEMON_SETTINGS = POKEMON[HoloPokemonId.ZORUA][HoloPokemonForm(0)]
ZORUA_SIZE_SETTINGS = EXTENDED[HoloPokemonId.ZORUA][HoloPokemonForm(0)].size_settings


def zorua_size(
    wild_zorua_weight_kg: float,
    wild_zorua_height_m: float,
    wild_zorua_size_class: SizeClass,
    buddy_pokemon_settings: PokemonSettings,
    buddy_size_settings: SizeSettings,
):
    if not wild_zorua_size_class.in_bounds(wild_zorua_height_m, ZORUA_SIZE_SETTINGS):
        lower, upper = wild_zorua_size_class.get_bounds(ZORUA_SIZE_SETTINGS)
        raise ValueError(
            f"Size class mismatch: Zorua with height {wild_zorua_height_m}m "
            f"cannot be {wild_zorua_size_class} ([{lower}, {upper}])"
        )

    power = 1 if wild_zorua_size_class == SizeClass.XXL else 2

    wild_buddy_height_variant = wild_zorua_height_m / buddy_pokemon_settings.pokedex_height_m
    avg_weight = wild_buddy_height_variant**power * buddy_pokemon_settings.pokedex_weight_kg
    weight_index = (wild_zorua_weight_kg - avg_weight) / buddy_pokemon_settings.weight_std_dev

    buddy_size_class = SizeClass.from_height(wild_zorua_height_m, buddy_size_settings)
    power = 1 if buddy_size_class == SizeClass.XXL else 2

    zorua_height_variant = min(max(wild_buddy_height_variant, 0.49), 1.75)
    zorua_avg_weight = zorua_height_variant**power * ZORUA_POKEMON_SETTINGS.pokedex_weight_kg

    zorua_weight = zorua_avg_weight + weight_index * ZORUA_POKEMON_SETTINGS.weight_std_dev
    zorua_height = zorua_height_variant * ZORUA_POKEMON_SETTINGS.pokedex_height_m

    if zorua_weight <= 0:
        zorua_weight = zorua_avg_weight

    # TODO Verify if it should be the same as `buddy_size_class`
    # Note: No, it is not the same on sus pokemons (+pumpkaboo, h-lilligant, h-avalugg, etc)
    zorua_size_class = SizeClass.from_height(wild_zorua_height_m, buddy_size_settings)

    return (zorua_weight, zorua_height, zorua_size_class)
