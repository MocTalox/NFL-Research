from __future__ import annotations

from dataclasses import dataclass

from nfl.data import (
    EXTENDED,
    POKEMON,
    PokeSpecies,
    SizeClass,
    get_temp_evo_pokemon_settings,
    get_temp_evo_size_settings,
)
from nfl.exceptions import ValidationError
from nfl.proto import HoloTempEvoId, PokemonSettings, SizeSettings
from nfl.utils import has_decimals


@dataclass(frozen=True)
class SizedPokemonInfo:
    pokemon_id: PokeSpecies
    pokemon_settings: PokemonSettings
    size_settings: SizeSettings

    @classmethod
    def build_info(cls, pokemon: PokeSpecies) -> SizedPokemonInfo:
        pokemon_settings = POKEMON.get(pokemon)
        pokemon_extended_settings = EXTENDED.get(pokemon)
        assert pokemon_settings and pokemon_extended_settings

        if pokemon.temp_evo:
            pokemon_settings = get_temp_evo_pokemon_settings(
                pokemon_settings, pokemon.temp_evo
            )
            size_settings = get_temp_evo_size_settings(
                pokemon_extended_settings, pokemon.temp_evo
            )
        else:
            size_settings = pokemon_extended_settings.size_settings

        return cls(pokemon, pokemon_settings, size_settings)


@dataclass(frozen=True)
class SizedPokemon(SizedPokemonInfo):
    weight_kg: float
    height_m: float
    size_class: SizeClass

    @classmethod
    def build(
        cls,
        pokemon: PokeSpecies,
        weight_kg: float,
        height_m: float,
        size_class: SizeClass | None = None,
    ) -> SizedPokemon:
        if weight_kg < 0 or height_m < 0:
            raise ValidationError(
                f"Invalid Pokémon dimensions: weight_kg={weight_kg}, height_m={height_m}. "
                f"Values must be positive."
            )

        pokemon_info = SizedPokemonInfo.build_info(pokemon)

        if size_class is None:
            size_class = SizeClass.from_height(height_m, pokemon_info.size_settings)
        else:
            candidates = (
                (height_m - 0.005, height_m + 0.005)
                if has_decimals(height_m, 2)
                else (height_m,)
            )
            if not any(
                size_class.in_bounds(h, pokemon_info.size_settings) for h in candidates
            ):
                lower, upper = size_class.get_bounds(pokemon_info.size_settings)
                raise ValidationError(
                    f"Size class mismatch: {pokemon} with height {height_m}m "
                    f"cannot be {size_class} ([{lower}, {upper}])"
                )

        return cls(
            pokemon_info.pokemon_id,
            pokemon_info.pokemon_settings,
            pokemon_info.size_settings,
            weight_kg,
            height_m,
            size_class,
        )

    def change_size(self, d_weight: float, d_height: float) -> SizedPokemon:
        height_min, height_max = self.size_class.get_bounds(self.size_settings)

        weight = max(self.weight_kg + d_weight, 0)
        height = max(min(self.height_m + d_height, height_max), height_min)

        return SizedPokemon(
            self.pokemon_id,
            self.pokemon_settings,
            self.size_settings,
            weight,
            height,
            self.size_class,
        )


def _resolve_evo_settings(
    evo_pokemon: SizedPokemonInfo | PokeSpecies | HoloTempEvoId,
    base_pokemon: SizedPokemonInfo,
):
    if isinstance(evo_pokemon, HoloTempEvoId):
        evo_pokemon = PokeSpecies(
            name=base_pokemon.pokemon_id.name,
            form=base_pokemon.pokemon_id.form,
            temp_evo=evo_pokemon,
        )
    if isinstance(evo_pokemon, PokeSpecies):
        evo_pokemon = SizedPokemonInfo.build_info(evo_pokemon)
    return evo_pokemon


def _lerp(value: float, a_min: float, a_max: float, b_min: float, b_max: float):
    return b_min + (b_max - b_min) * (value - a_min) / (a_max - a_min)


def evolution_size(
    pokemon: SizedPokemon, evo_pokemon: SizedPokemonInfo | PokeSpecies | HoloTempEvoId
) -> SizedPokemon:
    evo_pokemon = _resolve_evo_settings(evo_pokemon, pokemon)

    temp_evo_xxl_glitch = evo_pokemon.pokemon_id.temp_evo
    power = 1 if pokemon.size_class == SizeClass.XXL and not temp_evo_xxl_glitch else 2

    evo_height = _lerp(
        pokemon.height_m,
        *pokemon.size_class.get_bounds(pokemon.size_settings),
        *pokemon.size_class.get_bounds(evo_pokemon.size_settings),
    )

    height_variant = pokemon.height_m / pokemon.pokemon_settings.pokedex_height_m
    avg_weight = height_variant**power * pokemon.pokemon_settings.pokedex_weight_kg
    weight_index = (
        pokemon.weight_kg - avg_weight
    ) / pokemon.pokemon_settings.weight_std_dev

    evo_height_variant = evo_height / evo_pokemon.pokemon_settings.pokedex_height_m
    evo_avg_weight = (
        evo_height_variant**power * evo_pokemon.pokemon_settings.pokedex_weight_kg
    )
    evo_weight = (
        evo_avg_weight + weight_index * evo_pokemon.pokemon_settings.weight_std_dev
    )

    if evo_weight <= 0:
        evo_weight = evo_pokemon.pokemon_settings.pokedex_weight_kg

    size_class = SizeClass.from_height(
        evo_height,
        pokemon.size_settings if temp_evo_xxl_glitch else evo_pokemon.size_settings,
    )

    return SizedPokemon(
        evo_pokemon.pokemon_id,
        evo_pokemon.pokemon_settings,
        evo_pokemon.size_settings,
        evo_weight,
        evo_height,
        size_class,
    )


def evolution_size_range(
    pokemon: SizedPokemon,
    evo_pokemon: SizedPokemonInfo | PokeSpecies | HoloTempEvoId,
) -> dict[str, SizedPokemon | dict[str, float | SizeClass]]:
    evo_pokemon = _resolve_evo_settings(evo_pokemon, pokemon)

    min_min = evolution_size(pokemon.change_size(-0.005, -0.005), evo_pokemon)
    min_max = evolution_size(pokemon.change_size(-0.005, 0.005), evo_pokemon)
    max_min = evolution_size(pokemon.change_size(0.005, -0.005), evo_pokemon)
    max_max = evolution_size(pokemon.change_size(0.005, 0.005), evo_pokemon)

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

    return {
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
