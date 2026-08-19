from dataclasses import replace

from nfl.proto import (
    COMBAT_MOVE,
    FORM_SETTINGS,
    FRIENDSHIP_MILESTONE_SETTINGS,
    MOVE_SETTINGS,
    NON_COMBAT_MOVE_SETTINGS,
    PLAYER_LEVEL,
    POKEMON_EXTENDED_SETTINGS,
    POKEMON_SETTINGS,
    ROCKET_SETTINGS,
    STATIONED_POKEMON_TABLE_SETTINGS,
    TYPE_EFFECTIVE,
    WEATHER_AFFINITIES,
    HoloCharacterCategory,
    HoloPokemonMove,
    HoloTempEvoId,
    HoloWeatherCondition,
    PokemonExtendedSettings,
    PokemonSettings,
    SizeSettings,
)

from ._poke_map import get_poke, to_poke_map
from .poke_species import PokeSpecies


def _get_non_combat_move_attack_defense_bonus(move: HoloPokemonMove):
    move_ae = NON_COMBAT_MOVES[move].bonus_effect
    assert move_ae.attack_defense_bonus
    return move_ae.attack_defense_bonus.attributes


CPM = [cpm for cpm in PLAYER_LEVEL.cp_multiplier]
RCPM = [cpm for cpm in ROCKET_SETTINGS.cp_multiplier]
RANKS = {rank.character_category: rank for rank in ROCKET_SETTINGS.rank}
POKEMON = to_poke_map(POKEMON_SETTINGS, lambda p: p.pokemon_id, lambda p: p.form)
EXTENDED = to_poke_map(
    POKEMON_EXTENDED_SETTINGS, lambda p: p.unique_id, lambda p: p.form
)
FORMS = {fs.pokemon: [form.form for form in fs.forms] for fs in FORM_SETTINGS}
FORM_POKEMON = {form.form: fs.pokemon for fs in FORM_SETTINGS for form in fs.forms}
PVE_MOVES = {move.movement_id: move for move in MOVE_SETTINGS}
PVP_MOVES = {move.unique_id: move for move in COMBAT_MOVE}
NON_COMBAT_MOVES = {move.unique_id: move for move in NON_COMBAT_MOVE_SETTINGS}
TYPES = {te.attack_type: te for te in TYPE_EFFECTIVE}
WEATHER = {wa.weather_condition: wa for wa in WEATHER_AFFINITIES}
TYPES_WEATHER = {
    pt: wa.weather_condition for wa in WEATHER_AFFINITIES for pt in wa.pokemon_type
}
FRIENDSHIP = {fms.friendship_level: fms for fms in FRIENDSHIP_MILESTONE_SETTINGS}
FRIENDSHIP_DMG_BONUS = {fs: FRIENDSHIP[fs].attack_bonus_percentage for fs in FRIENDSHIP}
HELPERS = {tb.num_stationed: tb for tb in STATIONED_POKEMON_TABLE_SETTINGS.tier_boosts}
HELPERS_DMG_BONUS = {tb: HELPERS[tb].hundredths_of_percent for tb in HELPERS}
BEHEMOTH_BLADE_AE = {
    combat_type: attributes.attack_multiplier
    for attributes in _get_non_combat_move_attack_defense_bonus(
        HoloPokemonMove.BEHEMOTH_BLADE
    )
    for combat_type in attributes.combat_types
}
BEHEMOTH_BASH_AE = {
    combat_type: attributes.defense_multiplier
    for attributes in _get_non_combat_move_attack_defense_bonus(
        HoloPokemonMove.BEHEMOTH_BASH
    )
    for combat_type in attributes.combat_types
}


def get_tgr_rank_mult(character_category: HoloCharacterCategory) -> float:
    if character_category not in RANKS:
        raise ValueError(f"No rank multiplier configured for {character_category}")
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
    glitched: bool = False,
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
        temp_evo_overrides.size_settings
        if not glitched
        else SizeSettings(
            pokemon_extended_settings.size_settings.xxs_lower_bound,
            pokemon_extended_settings.size_settings.xs_lower_bound,
            pokemon_extended_settings.size_settings.m_lower_bound,
            pokemon_extended_settings.size_settings.m_upper_bound,
            temp_evo_overrides.size_settings.xl_upper_bound,
            temp_evo_overrides.size_settings.xxl_upper_bound,
        )
    )
