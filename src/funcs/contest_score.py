from dataclasses import dataclass

from core.gm_templates import CONTEST_SETTINGS
from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.pokemon_extended_settings import SizeSettings
from utils.utils import f32


height_coefficient = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.height_coefficient
weight_coefficient = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.weight_coefficient
iv_coefficient = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.iv_coefficient
xxl_adjustment_factor = CONTEST_SETTINGS.contest_score_coefficient.pokemon_size.xxl_adjustment_factor

@dataclass
class Pokemon:
    individual_values: int
    weight_kg: float
    height_m: float
    is_xxl: bool

def contest_score(pokemon: Pokemon, pokemon_settings: PokemonSettings, size_settings: SizeSettings):
    max_height = (
        size_settings.xxl_upper_bound
        if size_settings
        else f32(pokemon_settings.pokedex_height_m * f32(1.55))
    )

    height_scale = f32(max_height / pokemon_settings.pokedex_height_m)

    max_weight = f32(
        f32(pokemon_settings.pokedex_weight_kg * height_scale)
        + f32(pokemon_settings.weight_std_dev * f32(4.0))
    )

	# Value `0.853658536585366` comes from  `1.75 / 2.05`
    xxl_adjustment = (
        (weight_coefficient * 0.853658536585366 + iv_coefficient) * xxl_adjustment_factor
        if pokemon.is_xxl
        else 0.0
    )

    iv_ratio = f32(pokemon.individual_values / f32(45.0))
    weight_ratio = f32(pokemon.weight_kg / max_weight)
    height_ratio = f32(pokemon.height_m / max_height)

    return f32(
        xxl_adjustment
        + iv_coefficient * iv_ratio
        + weight_coefficient * weight_ratio
        + height_coefficient * height_ratio
    )
