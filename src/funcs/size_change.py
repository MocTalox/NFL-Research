from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from enum import Enum
from functools import total_ordering
from operator import attrgetter

from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.pokemon_extended_settings import PokemonExtendedSettings, SizeSettings
from funcs.temp_evo import temp_evo_pokemon_settings, temp_evo_size_settings, TempEvolutions


@dataclass
class Pokemon:
    pokemon_settings: PokemonSettings
    pokemon_extended_settings: PokemonExtendedSettings
    weight_kg: float
    height_m: float
    size_class: SizeClass

    def change_size(self, d_weight: float, d_height: float) -> Pokemon:
        height_min, height_max = self.size_class.bounds(self.pokemon_extended_settings.size_settings)

        weight = max(self.weight_kg + d_weight, 0)
        height = max(min(self.height_m + d_height, height_max), height_min)

        return Pokemon(
            self.pokemon_settings,
            self.pokemon_extended_settings,
            weight, height, self.size_class,
        )

@total_ordering
class SizeClass(Enum):
    XXS = (-2, attrgetter("xxs_lower_bound", "xs_lower_bound"))
    XS = (-1, attrgetter("xs_lower_bound", "m_lower_bound"))
    M = (0, attrgetter("m_lower_bound", "m_upper_bound"))
    XL = (1, attrgetter("m_upper_bound", "xl_upper_bound"))
    XXL = (2, attrgetter("xl_upper_bound", "xxl_upper_bound"))

    def __init__(self, id: int, bounds: Callable[[SizeSettings], tuple[float, float]]):
        self._ordinal = id
        self._bounds = bounds

    def __str__(self):
        return self.name

    def __lt__(self, other: SizeClass):
        return self._ordinal < other._ordinal

    def bounds(self, size_settings: SizeSettings):
        return self._bounds(size_settings)

    def in_bounds(self, height: float, size_settings: SizeSettings):
        height_min, height_max = self.bounds(size_settings)
        return (
            (self is SizeClass.XXS or height_min <= height)
            and
            (self is SizeClass.XXL or height < height_max)
        )

    @classmethod
    def from_height(cls, height: float, size_settings: SizeSettings):
        return next(size for size in cls if size.in_bounds(height, size_settings))

def _lerp(value: float, a_min: float, a_max: float, b_min: float, b_max: float):
    return b_min + (b_max - b_min) * (value - a_min) / (a_max - a_min)

def evolution_size(
    pokemon: Pokemon,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    temp_evo_xxl_glitch: bool = False,
):
    hei_wei_rel = 1 if pokemon.size_class == SizeClass.XXL and not temp_evo_xxl_glitch else 2

    evo_height = _lerp(
        pokemon.height_m,
        *pokemon.size_class.bounds(pokemon.pokemon_extended_settings.size_settings),
        *pokemon.size_class.bounds(evo_size_settings),
    )

    height_variant = pokemon.height_m / pokemon.pokemon_settings.pokedex_height_m
    avg_weight = height_variant**hei_wei_rel * pokemon.pokemon_settings.pokedex_weight_kg
    weight_index = (pokemon.weight_kg - avg_weight) / pokemon.pokemon_settings.weight_std_dev

    evo_height_variant = evo_height / evo_pokemon_settings.pokedex_height_m
    evo_avg_weight = evo_height_variant**hei_wei_rel * evo_pokemon_settings.pokedex_weight_kg
    evo_weight = evo_avg_weight + weight_index * evo_pokemon_settings.weight_std_dev

    if evo_weight <= 0:
        evo_weight = evo_avg_weight

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

def temp_evolution_size(pokemon: Pokemon, temp_evo_id: str | TempEvolutions):
    evo_pokemon_settings = temp_evo_pokemon_settings(pokemon.pokemon_settings, temp_evo_id)
    evo_size_settings = temp_evo_size_settings(pokemon.pokemon_extended_settings, temp_evo_id)

    return evolution_size(pokemon, evo_pokemon_settings, evo_size_settings, True)

def temp_evolution_size_range(pokemon: Pokemon, temp_evo_id: str | TempEvolutions):
    evo_pokemon_settings = temp_evo_pokemon_settings(pokemon.pokemon_settings, temp_evo_id)
    evo_size_settings = temp_evo_size_settings(pokemon.pokemon_extended_settings, temp_evo_id)

    return evolution_size_range(pokemon, evo_pokemon_settings, evo_size_settings, True)
