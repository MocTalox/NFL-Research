from dataclasses import replace

from core.gm_holoholo import HoloPokemonMove, HoloWeatherCondition, HoloTempEvoId
from core.gm_templates import FRIENDSHIP_MILESTONE_SETTINGS, TYPE_EFFECTIVE, WEATHER_AFFINITIES, PLAYER_LEVEL, POKEMON_SETTINGS, MOVE_SETTINGS, POKEMON_EXTENDED_SETTINGS
from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.pokemon_extended_settings import PokemonExtendedSettings, SizeSettings
from utils.poke_map import to_poke_map, get_poke
from utils.poke_species import PokeSpecies


CPM = [cpm for cpm in PLAYER_LEVEL.cp_multiplier]
POKEMON = to_poke_map(POKEMON_SETTINGS, lambda p: p.pokemon_id, lambda p: p.form)
EXTENDED = to_poke_map(POKEMON_EXTENDED_SETTINGS, lambda p: p.unique_id, lambda p: p.form)
MOVES = {move.movement_id: move for move in MOVE_SETTINGS}
TYPES = {te.attack_type: te for te in TYPE_EFFECTIVE}
WEATHER = {wa.weather_condition: wa for wa in WEATHER_AFFINITIES}
TYPES_WEATHER = {pt: wa.weather_condition for wa in WEATHER_AFFINITIES for pt in wa.pokemon_type}
FRIENDSHIP = [fms.attack_bonus_percentage for fms in sorted(
    FRIENDSHIP_MILESTONE_SETTINGS,
    key=lambda fms: fms.min_points_to_reach + fms.relative_points_to_reach,
)]


def get_pokemon_settings(poke: PokeSpecies) -> PokemonSettings | None:
    return get_poke(POKEMON, poke.name, poke.form)

def get_pokemon_extended_settings(poke: PokeSpecies) -> PokemonExtendedSettings | None:
    return get_poke(EXTENDED, poke.name, poke.form)

def get_move_boosting_weather(move: HoloPokemonMove) -> HoloWeatherCondition:
    return TYPES_WEATHER[MOVES[move].pokemon_type]

def get_temp_evo_pokemon_settings(
    pokemon_settings: PokemonSettings,
    temp_evo_id: HoloTempEvoId,
):
    temp_evo_overrides = next(
        (
            temp_evo_overrides
            for temp_evo_overrides in pokemon_settings.temp_evo_overrides
            if temp_evo_overrides.temp_evo_id == temp_evo_id
        ),
        None,
    )

    if not temp_evo_overrides:
        raise ValueError()

    return replace(
        pokemon_settings,
        type=temp_evo_overrides.type_override_1,
        type_2=temp_evo_overrides.type_override_2,
        stats=temp_evo_overrides.stats,
        pokedex_height_m=temp_evo_overrides.average_height_m,
        pokedex_weight_kg=temp_evo_overrides.average_weight_kg,
    )

def get_temp_evo_size_settings(
    pokemon_extended_settings: PokemonExtendedSettings,
    temp_evo_id: HoloTempEvoId,
    glitched: bool = True,
):
    temp_evo_overrides = next(
        (
            temp_evo_overrides
            for temp_evo_overrides in pokemon_extended_settings.temp_evo_overrides
            if temp_evo_overrides.temp_evo_id == temp_evo_id
        ),
        None,
    )

    if not temp_evo_overrides:
        raise ValueError()

    return (
        SizeSettings(
            pokemon_extended_settings.size_settings.xxs_lower_bound,
            pokemon_extended_settings.size_settings.xs_lower_bound,
            pokemon_extended_settings.size_settings.m_lower_bound,
            pokemon_extended_settings.size_settings.m_upper_bound,
            temp_evo_overrides.size_settings.xl_upper_bound,
            temp_evo_overrides.size_settings.xxl_upper_bound,
        )
        if glitched
        else temp_evo_overrides.size_settings
    )
