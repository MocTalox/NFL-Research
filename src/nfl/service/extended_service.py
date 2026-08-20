"""
float hei = poke.avgHeight, wei = poke.avgWeight, max = poke.xxlUpperBound;
float aux = (800 / max + 150 / (max + hei * 0.5f));
float h = (pts - 178) / aux, w = h * (wei / hei);
return new float[] { w, h };
"""

from dataclasses import dataclass

from nfl.data import (
    POKEMON,
    PokeData,
    PokeSpecies,
    get_pokemon_extended_settings,
)
from nfl.proto import PokemonExtendedSettings, PokemonSettings


@dataclass(frozen=True)
class _PokemonData(PokeSpecies):
    pokedex_height_m: float
    pokedex_weight_kg: float
    height_std_dev: float
    weight_std_dev: float
    xxs_lower_bound: float
    xs_lower_bound: float
    m_lower_bound: float
    m_upper_bound: float
    xl_upper_bound: float
    xxl_upper_bound: float

    def is_the_same(self, other: PokeSpecies) -> bool:
        if not isinstance(other, _PokemonData):
            return False
        if self is other:
            return True
        return (
            self.name == other.name
            and self.temp_evo == other.temp_evo
            and self.shadow == other.shadow
            and self.pokedex_height_m == other.pokedex_height_m
            and self.pokedex_weight_kg == other.pokedex_weight_kg
            and self.height_std_dev == other.height_std_dev
            and self.weight_std_dev == other.weight_std_dev
            and self.xxs_lower_bound == other.xxs_lower_bound
            and self.xs_lower_bound == other.xs_lower_bound
            and self.m_lower_bound == other.m_lower_bound
            and self.m_upper_bound == other.m_upper_bound
            and self.xl_upper_bound == other.xl_upper_bound
            and self.xxl_upper_bound == other.xxl_upper_bound
        )


def _to_pokemon_data(
    pokemon_settings: PokemonSettings,
    pokemon_extended_settings: PokemonExtendedSettings,
):

    return _PokemonData(
        name=pokemon_settings.pokemon_id,
        form=pokemon_settings.form,
        pokedex_height_m=pokemon_settings.pokedex_height_m,
        pokedex_weight_kg=pokemon_settings.pokedex_weight_kg,
        height_std_dev=pokemon_settings.height_std_dev,
        weight_std_dev=pokemon_settings.weight_std_dev,
        xxs_lower_bound=pokemon_extended_settings.size_settings.xxs_lower_bound,
        xs_lower_bound=pokemon_extended_settings.size_settings.xs_lower_bound,
        m_lower_bound=pokemon_extended_settings.size_settings.m_lower_bound,
        m_upper_bound=pokemon_extended_settings.size_settings.m_upper_bound,
        xl_upper_bound=pokemon_extended_settings.size_settings.xl_upper_bound,
        xxl_upper_bound=pokemon_extended_settings.size_settings.xxl_upper_bound,
    )


def _unfold_settings(pokemon_settings: PokemonSettings) -> list[_PokemonData]:

    poke = PokeSpecies(
        name=pokemon_settings.pokemon_id,
        form=pokemon_settings.form,
    )
    pokemon_extended_settings = get_pokemon_extended_settings(poke)

    if not pokemon_extended_settings:
        return []
    return [
        _to_pokemon_data(pokemon_settings, pokemon_extended_settings),
    ]


_POKEMON_DATA: PokeData[_PokemonData] = PokeData(POKEMON, _unfold_settings)


def get_all_pokemon() -> list[PokeSpecies]:
    return sorted(_POKEMON_DATA.get_all_species())
