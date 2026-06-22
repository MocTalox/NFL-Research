from __future__ import annotations

from dataclasses import dataclass

from core.gm_holoholo import HoloTempEvoId
from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.pokemon_extended_settings import PokemonExtendedSettings, SizeSettings
from service.common.data import get_temp_evo_pokemon_settings, get_temp_evo_size_settings
from service.common.size_class import SizeClass


@dataclass
class Pokemon:
    pokemon_settings: PokemonSettings
    pokemon_extended_settings: PokemonExtendedSettings
    weight_kg: float
    height_m: float
    size_class: SizeClass

    def change_size(self, d_weight: float, d_height: float) -> Pokemon:
        height_min, height_max = self.size_class.get_bounds(self.pokemon_extended_settings.size_settings)

        weight = max(self.weight_kg + d_weight, 0)
        height = max(min(self.height_m + d_height, height_max), height_min)

        return Pokemon(
            self.pokemon_settings,
            self.pokemon_extended_settings,
            weight, height, self.size_class,
        )

def _lerp(value: float, a_min: float, a_max: float, b_min: float, b_max: float):
    return b_min + (b_max - b_min) * (value - a_min) / (a_max - a_min)

def evolution_size(
    pokemon: Pokemon,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    temp_evo_xxl_glitch: bool = False,
):
    if not pokemon.size_class.in_bounds(pokemon.height_m, pokemon.pokemon_extended_settings.size_settings):
        raise ValueError()

    hei_wei_rel = 1 if pokemon.size_class == SizeClass.XXL and not temp_evo_xxl_glitch else 2

    evo_height = _lerp(
        pokemon.height_m,
        *pokemon.size_class.get_bounds(pokemon.pokemon_extended_settings.size_settings),
        *pokemon.size_class.get_bounds(evo_size_settings),
    )

    height_variant = pokemon.height_m / pokemon.pokemon_settings.pokedex_height_m
    avg_weight = height_variant**hei_wei_rel * pokemon.pokemon_settings.pokedex_weight_kg
    weight_index = (pokemon.weight_kg - avg_weight) / pokemon.pokemon_settings.weight_std_dev

    evo_height_variant = evo_height / evo_pokemon_settings.pokedex_height_m
    evo_avg_weight = evo_height_variant**hei_wei_rel * evo_pokemon_settings.pokedex_weight_kg
    evo_weight = evo_avg_weight + weight_index * evo_pokemon_settings.weight_std_dev

    if evo_weight <= 0:
        evo_weight = evo_pokemon_settings.pokedex_weight_kg

    size_class = SizeClass.from_height(
        evo_height,
        pokemon.pokemon_extended_settings.size_settings
        if temp_evo_xxl_glitch else evo_size_settings,
    )

    return (evo_weight, evo_height, size_class)

def evolution_size_range(
    pokemon: Pokemon,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    temp_evo_xxl_glitch: bool = False,
):
    weight_min_min, height_min_min, size_min_min = evolution_size(
        pokemon.change_size(-0.005, -0.005),
        evo_pokemon_settings,
        evo_size_settings,
        temp_evo_xxl_glitch,
    )

    weight_min_max, height_min_max, size_min_max = evolution_size(
        pokemon.change_size(-0.005, 0.005),
        evo_pokemon_settings,
        evo_size_settings,
        temp_evo_xxl_glitch,
    )

    weight_max_min, height_max_min, size_max_min = evolution_size(
        pokemon.change_size(0.005, -0.005),
        evo_pokemon_settings,
        evo_size_settings,
        temp_evo_xxl_glitch,
    )

    weight_max_max, height_max_max, size_max_max = evolution_size(
        pokemon.change_size(0.005, 0.005),
        evo_pokemon_settings,
        evo_size_settings,
        temp_evo_xxl_glitch,
    )

    weight_min = min(weight_min_min, weight_min_max, weight_max_min, weight_max_max)
    weight_max = max(weight_min_min, weight_min_max, weight_max_min, weight_max_max)
    height_min = min(height_min_min, height_min_max, height_max_min, height_max_max)
    height_max = max(height_min_min, height_min_max, height_max_min, height_max_max)
    size_min = min(size_min_min, size_min_max, size_max_min, size_max_max)
    size_max = max(size_min_min, size_min_max, size_max_min, size_max_max)
    return (
        (weight_min, weight_max),
        (height_min, height_max),
        (size_min, size_max),
    )

def temp_evolution_size(pokemon: Pokemon, temp_evo_id: HoloTempEvoId):
    evo_pokemon_settings = get_temp_evo_pokemon_settings(pokemon.pokemon_settings, temp_evo_id)
    evo_size_settings = get_temp_evo_size_settings(pokemon.pokemon_extended_settings, temp_evo_id)

    return evolution_size(pokemon, evo_pokemon_settings, evo_size_settings, True)

def temp_evolution_size_range(pokemon: Pokemon, temp_evo_id: HoloTempEvoId):
    evo_pokemon_settings = get_temp_evo_pokemon_settings(pokemon.pokemon_settings, temp_evo_id)
    evo_size_settings = get_temp_evo_size_settings(pokemon.pokemon_extended_settings, temp_evo_id)

    return evolution_size_range(pokemon, evo_pokemon_settings, evo_size_settings, True)
