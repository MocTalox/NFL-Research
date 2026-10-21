from nfl.data import (
    CONTEST_SETTINGS,
    PokeSpecies,
    get_pokemon_settings,
    get_size_settings,
)
from nfl.models import SizeClass, SizeData
from nfl.proto import PokemonSettings, SizeSettings

_CONTEST_SCORE_COEFFICIENT = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size
_HEIGHT_COEFFICIENT = _CONTEST_SCORE_COEFFICIENT.height_coefficient
_WEIGHT_COEFFICIENT = _CONTEST_SCORE_COEFFICIENT.weight_coefficient
_IV_COEFFICIENT = _CONTEST_SCORE_COEFFICIENT.iv_coefficient
_XXL_ADJUSTMENT_FACTOR = _CONTEST_SCORE_COEFFICIENT.xxl_adjustment_factor
_XXL_ADJUSTMENT_VALUE = (
    _WEIGHT_COEFFICIENT * 0.853658536585366 + _IV_COEFFICIENT
) * _XXL_ADJUSTMENT_FACTOR
# Value `0.853658536585366` comes from  `1.75 / 2.05`


def contest_score(
    pokemon: PokeSpecies,
    individual_values: int,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
):
    pokemon_settings = get_pokemon_settings(pokemon)
    size_settings = get_size_settings(pokemon)
    pokemon_size_data = SizeData.build(size_settings, weight_kg, height_m, size_class)

    return contest_score_formula(
        pokemon_settings,
        size_settings,
        individual_values,
        pokemon_size_data,
    )


def contest_score_formula(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings | None,
    individual_values: int,
    pokemon_size_data: SizeData,
):
    weight = pokemon_size_data.weight_kg
    height = pokemon_size_data.height_m
    size_class = pokemon_size_data.size_class

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

    xxl_adjustment = _XXL_ADJUSTMENT_VALUE if size_class == SizeClass.XXL else 0.0
    iv_ratio = individual_values / 45
    weight_ratio = weight / max_weight
    height_ratio = height / max_height

    return (
        xxl_adjustment
        + _IV_COEFFICIENT * iv_ratio
        + _WEIGHT_COEFFICIENT * weight_ratio
        + _HEIGHT_COEFFICIENT * height_ratio
    )


def contest_score_range(
    pokemon: PokeSpecies,
    individual_values: int,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
):
    pokemon_settings = get_pokemon_settings(pokemon)
    size_settings = get_size_settings(pokemon)
    pokemon_size_data = SizeData.build(size_settings, weight_kg, height_m, size_class)

    min_min = contest_score_formula(
        pokemon_settings,
        size_settings,
        individual_values,
        pokemon_size_data.change_size(size_settings, -0.005, -0.005),
    )
    min_max = contest_score_formula(
        pokemon_settings,
        size_settings,
        individual_values,
        pokemon_size_data.change_size(size_settings, -0.005, 0.005),
    )
    max_min = contest_score_formula(
        pokemon_settings,
        size_settings,
        individual_values,
        pokemon_size_data.change_size(size_settings, 0.005, -0.005),
    )
    max_max = contest_score_formula(
        pokemon_settings,
        size_settings,
        individual_values,
        pokemon_size_data.change_size(size_settings, 0.005, 0.005),
    )

    score_min = min(min_min, min_max, max_min, max_max)
    score_max = max(min_min, min_max, max_min, max_max)

    return score_min, score_max
