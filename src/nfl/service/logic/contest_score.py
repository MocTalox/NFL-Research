from dataclasses import dataclass

from nfl.proto import CONTEST_SETTINGS, PokemonSettings, SizeSettings
from nfl.service.common.size_class import SizeClass

height_coefficient = (
    CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.height_coefficient
)
weight_coefficient = (
    CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.weight_coefficient
)
iv_coefficient = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.iv_coefficient
xxl_adjustment_factor = (
    CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.xxl_adjustment_factor
)


@dataclass
class Pokemon:
    pokemon_settings: PokemonSettings
    size_settings: SizeSettings | None
    individual_values: int
    weight_kg: float
    height_m: float
    size_class: SizeClass


def contest_score(pokemon: Pokemon):
    max_height = (
        pokemon.size_settings.xxl_upper_bound
        if pokemon.size_settings
        else pokemon.pokemon_settings.pokedex_height_m * 1.55
    )

    height_scale = max_height / pokemon.pokemon_settings.pokedex_height_m

    max_weight = (
        pokemon.pokemon_settings.pokedex_weight_kg * height_scale
        + pokemon.pokemon_settings.weight_std_dev * 4
    )

    # Value `0.853658536585366` comes from  `1.75 / 2.05`
    xxl_adjustment = (
        (weight_coefficient * 0.853658536585366 + iv_coefficient)
        * xxl_adjustment_factor
        if pokemon.size_class == SizeClass.XXL
        else 0.0
    )

    iv_ratio = pokemon.individual_values / 45
    weight_ratio = pokemon.weight_kg / max_weight
    height_ratio = pokemon.height_m / max_height

    return (
        xxl_adjustment
        + iv_coefficient * iv_ratio
        + weight_coefficient * weight_ratio
        + height_coefficient * height_ratio
    )
