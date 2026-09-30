from nfl.data import (
    PokeSpecies,
    get_pokemon_settings,
    get_size_settings,
)
from nfl.models import SizeClass, SizeData, SizeDataRange
from nfl.proto import HoloTempEvoId, PokemonSettings, SizeSettings


def _lerp(value: float, a_min: float, a_max: float, b_min: float, b_max: float):
    return b_min + (b_max - b_min) * (value - a_min) / (a_max - a_min)


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
    )


def evolution_size_raw(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
) -> SizeData:
    pokemon_size_data = SizeData.build(size_settings, weight_kg, height_m, size_class)

    return evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data,
    )


def evolution_size_formula(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    pokemon_size_data: SizeData,
) -> SizeData:
    weight = pokemon_size_data.weight_kg
    height = pokemon_size_data.height_m
    size_class = pokemon_size_data.size_class
    temp_evo_xxl_glitch = bool(pokemon_settings.nfl_temp_evo_id)

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
) -> SizeDataRange:
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
    )


def evolution_size_range_raw(
    pokemon_settings: PokemonSettings,
    size_settings: SizeSettings,
    evo_pokemon_settings: PokemonSettings,
    evo_size_settings: SizeSettings,
    weight_kg: float,
    height_m: float,
    size_class: SizeClass | None = None,
) -> SizeDataRange:
    pokemon_size_data = SizeData.build(size_settings, weight_kg, height_m, size_class)

    lower_wei_lower_hei = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, -0.005, -0.005),
    )
    lower_wei_upper_hei = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, -0.005, 0.005),
    )
    upper_wei_lower_hei = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, 0.005, -0.005),
    )
    upper_wei_upper_hei = evolution_size_formula(
        pokemon_settings,
        size_settings,
        evo_pokemon_settings,
        evo_size_settings,
        pokemon_size_data.change_size(size_settings, 0.005, 0.005),
    )

    return SizeDataRange.build(
        lower_wei_lower_hei,
        lower_wei_upper_hei,
        upper_wei_lower_hei,
        upper_wei_upper_hei,
    )
