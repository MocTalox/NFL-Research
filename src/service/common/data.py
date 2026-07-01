from dataclasses import replace

from core.gm_holoholo import HoloPokemonMove, HoloWeatherCondition, HoloTempEvoId, HoloCharacterCategory
from core.gm_templates import FRIENDSHIP_MILESTONE_SETTINGS, TYPE_EFFECTIVE, WEATHER_AFFINITIES, PLAYER_LEVEL, POKEMON_SETTINGS, MOVE_SETTINGS, COMBAT_MOVE, POKEMON_EXTENDED_SETTINGS, ROCKET_SETTINGS, NON_COMBAT_MOVE_SETTINGS
from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.pokemon_extended_settings import PokemonExtendedSettings, SizeSettings
from utils.poke_map import to_poke_map, get_poke
from utils.poke_species import PokeSpecies


CPM = [cpm for cpm in PLAYER_LEVEL.cp_multiplier]
RCPM = [cpm for cpm in ROCKET_SETTINGS.cp_multiplier]
RANKS = {rank.character_category: rank for rank in ROCKET_SETTINGS.rank}
POKEMON = to_poke_map(POKEMON_SETTINGS, lambda p: p.pokemon_id, lambda p: p.form)
EXTENDED = to_poke_map(POKEMON_EXTENDED_SETTINGS, lambda p: p.unique_id, lambda p: p.form)
PVE_MOVES = {move.movement_id: move for move in MOVE_SETTINGS}
PVP_MOVES = {move.unique_id: move for move in COMBAT_MOVE}
NON_COMBAT_MOVES = {move.unique_id: move for move in NON_COMBAT_MOVE_SETTINGS}
TYPES = {te.attack_type: te for te in TYPE_EFFECTIVE}
WEATHER = {wa.weather_condition: wa for wa in WEATHER_AFFINITIES}
TYPES_WEATHER = {pt: wa.weather_condition for wa in WEATHER_AFFINITIES for pt in wa.pokemon_type}
FRIENDSHIP_DMG_BONUS = {fms.friendship_level: fms.attack_bonus_percentage for fms in FRIENDSHIP_MILESTONE_SETTINGS}
BEHEMOTH_BLADE_AE = {
    combat_type: attributes.attack_multiplier
    for attributes
    in NON_COMBAT_MOVES[HoloPokemonMove.BEHEMOTH_BLADE].bonus_effect.attack_defense_bonus.attributes
    for combat_type
    in attributes.combat_types
}
BEHEMOTH_BASH_AE = {
    combat_type: attributes.defense_multiplier
    for attributes
    in NON_COMBAT_MOVES[HoloPokemonMove.BEHEMOTH_BASH].bonus_effect.attack_defense_bonus.attributes
    for combat_type
    in attributes.combat_types
}

def get_tgr_rank_mult(character_category: HoloCharacterCategory) -> float:
    if character_category not in RANKS:
        raise ValueError(f"{character_category}") #TODO err msg
    return RANKS[character_category].rank_multiplier

def get_pokemon_settings(poke: PokeSpecies) -> PokemonSettings | None:
    return get_poke(POKEMON, poke.name, poke.form)

def get_pokemon_extended_settings(poke: PokeSpecies) -> PokemonExtendedSettings | None:
    return get_poke(EXTENDED, poke.name, poke.form)

def get_move_boosting_weather(move: HoloPokemonMove) -> HoloWeatherCondition:
    return TYPES_WEATHER[PVE_MOVES[move].pokemon_type]

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
        raise ValueError(
            f"Missing temporary evolution overrides for {pokemon_settings.pokemon_id} "
            f"({pokemon_settings.form}): {temp_evo_id}"
        )

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
        raise ValueError(
            f"Missing temporary evolution overrides for {pokemon_extended_settings.unique_id} "
            f"({pokemon_extended_settings.form}): {temp_evo_id}"
        )

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
