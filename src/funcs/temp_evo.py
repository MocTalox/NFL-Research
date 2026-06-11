from __future__ import annotations

from dataclasses import replace

from proto.msg.pokemon_settings import PokemonSettings
from proto.msg.pokemon_extended_settings import PokemonExtendedSettings, SizeSettings


class TempEvolutions:
    TEMP_EVOLUTION_MEGA = "TEMP_EVOLUTION_MEGA"
    TEMP_EVOLUTION_MEGA_X = "TEMP_EVOLUTION_MEGA_X"
    TEMP_EVOLUTION_MEGA_Y = "TEMP_EVOLUTION_MEGA_Y"
    TEMP_EVOLUTION_PRIMAL = "TEMP_EVOLUTION_PRIMAL"

def temp_evo_pokemon_settings(
    pokemon_settings: PokemonSettings,
    temp_evo_id: str | TempEvolutions,
):
    temp_evos = {teo.temp_evo_id: teo for teo in pokemon_settings.temp_evo_overrides}
    temp_evo_overrides = temp_evos.get(str(temp_evo_id))

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

def temp_evo_size_settings(
    pokemon_extended_settings: PokemonExtendedSettings,
    temp_evo_id: str | TempEvolutions,
    glitched: bool = True,
):
    temp_evos = {teo.temp_evo_id: teo for teo in pokemon_extended_settings.temp_evo_overrides}
    temp_evo_overrides = temp_evos.get(str(temp_evo_id))

    if not temp_evo_overrides:
        raise ValueError()

    return SizeSettings(
        pokemon_extended_settings.size_settings.xxs_lower_bound,
        pokemon_extended_settings.size_settings.xs_lower_bound,
        pokemon_extended_settings.size_settings.m_lower_bound,
        pokemon_extended_settings.size_settings.m_upper_bound,
        temp_evo_overrides.size_settings.xl_upper_bound,
        temp_evo_overrides.size_settings.xxl_upper_bound,
    ) if glitched else temp_evo_overrides.size_settings
