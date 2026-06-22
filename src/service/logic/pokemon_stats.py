from math import floor

from proto.msg.pokemon_settings import PokemonSettings
from service.common.data import CPM
from utils.float32 import f32


def get_cpm(level: float) -> float:
    if level % 1 == 0:
        return CPM[int(level) - 1]
    cpmPrevd, cpmNextd = get_cpm(level - 0.5), get_cpm(level + 0.5)
    return f32(((cpmPrevd**2 + cpmNextd**2) / 2)**0.5)

def get_cp(poke: PokemonSettings, cpm: float, iv_atk: int, iv_def: int, iv_sta: int) -> int:
    atk_stat = (poke.stats.base_attack + iv_atk) * cpm
    def_stat = (poke.stats.base_defense + iv_def) * cpm
    sta_stat = (poke.stats.base_stamina + iv_sta) * cpm
    return max(10, floor(atk_stat * (def_stat * sta_stat)**0.5 * 0.1))

def get_hp(poke: PokemonSettings, cpm: float, iv_sta: int) -> int:
    sta_stat = (poke.stats.base_stamina + iv_sta) * cpm
    return max(10, floor(sta_stat))

def get_tgr_cp(poke: PokemonSettings, cpm: float, rank: float, iv_atk: int, iv_def: int, iv_sta: int) -> int:
    atk_stat = floor((poke.stats.base_attack + iv_atk) * 5 / 3) * cpm * rank
    def_stat = (poke.stats.base_defense + iv_def) * cpm * rank
    sta_stat = floor((poke.stats.base_stamina + iv_sta) * 3 / 5) * cpm * rank
    return max(10, floor(atk_stat * (def_stat * sta_stat)**0.5 * 0.1))

def get_tgr_hp(poke: PokemonSettings, cpm: float, rank: float, iv_sta: int) -> int:
    sta_stat = floor((poke.stats.base_stamina + iv_sta) * 3 / 5) * cpm * rank
    return max(10, floor(sta_stat))
