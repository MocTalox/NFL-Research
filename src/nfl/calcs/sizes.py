from __future__ import annotations

from dataclasses import dataclass

from nfl.data import (
    PokeSpecies,
    SizeClass,
    get_pokemon_settings,
    get_size_settings,
)
from nfl.exceptions import ValidationError
from nfl.proto import HoloTempEvoId, PokemonSettings, SizeSettings
from nfl.utils import has_decimals


@dataclass(frozen=True)
class SizeData:
    weight_kg: float
    height_m: float
    size_class: SizeClass

    @classmethod
    def build(  # TODO make module-level private
        cls,
        size_settings: SizeSettings,
        weight_kg: float,
        height_m: float,
        size_class: SizeClass | None = None,
    ) -> SizeData:
        if weight_kg < 0 or height_m < 0:
            raise ValidationError(
                f"Invalid Pokémon dimensions: weight_kg={weight_kg}, height_m={height_m}. "
                f"Values must be positive."
            )

        if size_class is None:
            size_class = SizeClass.from_height(height_m, size_settings)
        else:
            _validate_size_class(size_settings, height_m, size_class)

        return cls(weight_kg, height_m, size_class)

    def change_size(  # TODO make module-level private
        self, size_settings: SizeSettings, d_weight: float, d_height: float
    ) -> SizeData:
        height_min, height_max = self.size_class.get_bounds(size_settings)

        weight = max(self.weight_kg + d_weight, 0)
        height = max(min(self.height_m + d_height, height_max), height_min)

        return SizeData(weight, height, self.size_class)


def _lerp(value: float, a_min: float, a_max: float, b_min: float, b_max: float):
    return b_min + (b_max - b_min) * (value - a_min) / (a_max - a_min)


def _validate_size_class(
    size_settings: SizeSettings, height_m: float, size_class: SizeClass
):
    candidates = (
        (height_m - 0.005, height_m + 0.005)
        if has_decimals(height_m, 2)
        else (height_m,)
    )
    if any(size_class.in_bounds(h, size_settings) for h in candidates):
        return
    lower, upper = size_class.get_bounds(size_settings)
    raise ValidationError(
        f"Size class mismatch: height_m={height_m} for the given Pokémon "
        f"cannot be {size_class} ([{lower}, {upper}])"
    )


def evolution_size(
    pokemon: PokeSpecies,
    evo_pokemon: PokeSpecies | HoloTempEvoId,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
    glitched_temp_evo: bool = False,
) -> SizeData:
    if isinstance(evo_pokemon, HoloTempEvoId):
        evo_pokemon = PokeSpecies(
            name=pokemon.name,
            form=pokemon.form,
            temp_evo=evo_pokemon,
        )

    pokemon_settings = get_pokemon_settings(pokemon)
    size_settings = get_size_settings(pokemon)
    evo_pokemon_settings = get_pokemon_settings(evo_pokemon)
    evo_size_settings = get_size_settings(evo_pokemon, glitched_temp_evo)

    return evolution_size_raw(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        weight_kg,
        height_m,
        size_class,
        bool(evo_pokemon.temp_evo),
    )


def evolution_size_raw(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
    temp_evo_xxl_glitch: bool = False,
) -> SizeData:
    pokemon_size_data = SizeData.build(size_settings, weight_kg, height_m, size_class)

    return evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data,
        temp_evo_xxl_glitch,
    )


def evolution_size_formula(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    pokemon_size_data: SizeData,
    temp_evo_xxl_glitch: bool = False,
) -> SizeData:
    weight = pokemon_size_data.weight_kg
    height = pokemon_size_data.height_m
    size_class = pokemon_size_data.size_class

    power = 2 if size_class != SizeClass.XXL or temp_evo_xxl_glitch else 1

    evo_height = _lerp(
        height,
        *size_class.get_bounds(size_settings),
        *size_class.get_bounds(evo_size_settings),
    )

    height_variant = height / pokemon_settings.pokedex_height_m
    avg_weight = height_variant**power * pokemon_settings.pokedex_weight_kg
    weight_index = (weight - avg_weight) / pokemon_settings.weight_std_dev

    evo_height_variant = evo_height / evo_pokemon_settings.pokedex_height_m
    evo_avg_weight = evo_height_variant**power * evo_pokemon_settings.pokedex_weight_kg
    evo_weight = evo_avg_weight + weight_index * evo_pokemon_settings.weight_std_dev

    if evo_weight <= 0:
        evo_weight = evo_pokemon_settings.pokedex_weight_kg

    size_class = SizeClass.from_height(
        evo_height,
        size_settings if temp_evo_xxl_glitch else evo_size_settings,
    )

    return SizeData(evo_weight, evo_height, size_class)


def evolution_size_range(
    pokemon: PokeSpecies,
    evo_pokemon: PokeSpecies | HoloTempEvoId,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
    glitched_temp_evo: bool = False,
) -> dict[str, SizeData | dict[str, float | SizeClass]]:
    if isinstance(evo_pokemon, HoloTempEvoId):
        evo_pokemon = PokeSpecies(
            name=pokemon.name,
            form=pokemon.form,
            temp_evo=evo_pokemon,
        )

    pokemon_settings = get_pokemon_settings(pokemon)
    size_settings = get_size_settings(pokemon)
    evo_pokemon_settings = get_pokemon_settings(evo_pokemon)
    evo_size_settings = get_size_settings(evo_pokemon, glitched_temp_evo)

    return evolution_size_range_raw(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        weight_kg,
        height_m,
        size_class,
        bool(evo_pokemon.temp_evo),
    )


def evolution_size_range_raw(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
    temp_evo_xxl_glitch: bool = False,
) -> dict[str, SizeData | dict[str, float | SizeClass]]:
    pokemon_size_data = SizeData.build(size_settings, weight_kg, height_m, size_class)

    min_min = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, -0.005, -0.005),
        temp_evo_xxl_glitch,
    )
    min_max = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, -0.005, 0.005),
        temp_evo_xxl_glitch,
    )
    max_min = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, 0.005, -0.005),
        temp_evo_xxl_glitch,
    )
    max_max = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, 0.005, 0.005),
        temp_evo_xxl_glitch,
    )

    weight_min = min(
        min_min.weight_kg, min_max.weight_kg, max_min.weight_kg, max_max.weight_kg
    )
    weight_max = max(
        min_min.weight_kg, min_max.weight_kg, max_min.weight_kg, max_max.weight_kg
    )
    height_min = min(
        min_min.height_m, min_max.height_m, max_min.height_m, max_max.height_m
    )
    height_max = max(
        min_min.height_m, min_max.height_m, max_min.height_m, max_max.height_m
    )
    size_class_min = min(
        min_min.size_class, min_max.size_class, max_min.size_class, max_max.size_class
    )
    size_class_max = max(
        min_min.size_class, min_max.size_class, max_min.size_class, max_max.size_class
    )

    return {  # TODO ugly object
        "min_min": min_min,
        "min_max": min_max,
        "max_min": max_min,
        "max_max": max_max,
        "weight": {
            "min": weight_min,
            "max": weight_max,
        },
        "height": {
            "min": height_min,
            "max": height_max,
        },
        "size_class": {
            "min": size_class_min,
            "max": size_class_max,
        },
    }
