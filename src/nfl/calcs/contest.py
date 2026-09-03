from nfl.data import (
    CONTEST_SETTINGS,
    PokeSpecies,
    SizeClass,
    get_pokemon_settings,
    get_size_settings,
)
from nfl.proto import PokemonSettings, SizeSettings

_CONTEST_SCORE_COEFFICIENT = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size
_HEIGHT_COEFFICIENT = _CONTEST_SCORE_COEFFICIENT.height_coefficient
_WEIGHT_COEFFICIENT = _CONTEST_SCORE_COEFFICIENT.weight_coefficient
_IV_COEFFICIENT = _CONTEST_SCORE_COEFFICIENT.iv_coefficient
_XXL_ADJUSTMENT_FACTOR = _CONTEST_SCORE_COEFFICIENT.xxl_adjustment_factor


def contest_score(
    pokemon: PokeSpecies,
    individual_values: int,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass,
):
    return contest_score_raw(
        get_pokemon_settings(pokemon),
        get_size_settings(pokemon),
        individual_values,
        weight_kg,
        height_m,
        size_class,
    )


def contest_score_raw(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings | None,
    individual_values: int,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass,
):
    max_height = (
        size_settings.xxl_upper_bound
        if size_settings
        else pokemon_settings.pokedex_height_m * 1.55
    )

    height_scale = max_height / pokemon_settings.pokedex_height_m

    max_weight = (
        pokemon_settings.pokedex_weight_kg * height_scale
        + pokemon_settings.weight_std_dev * 4
    )

    # Value `0.853658536585366` comes from  `1.75 / 2.05`
    xxl_adjustment = (
        (_WEIGHT_COEFFICIENT * 0.853658536585366 + _IV_COEFFICIENT)
        * _XXL_ADJUSTMENT_FACTOR
        if size_class == SizeClass.XXL
        else 0.0
    )

    iv_ratio = individual_values / 45
    weight_ratio = weight_kg / max_weight
    height_ratio = height_m / max_height

    return (
        xxl_adjustment
        + _IV_COEFFICIENT * iv_ratio
        + _WEIGHT_COEFFICIENT * weight_ratio
        + _HEIGHT_COEFFICIENT * height_ratio
    )
