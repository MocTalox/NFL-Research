from math import floor

from nfl.proto import HoloCharacterCategory, PokemonSettings
from nfl.service.common.data import CPM, RCPM, get_tgr_rank_mult
from nfl.utils import f32


def get_cpm(level: float) -> float:
    if level % 0.5 != 0:
        raise ValueError(
            f"Invalid level {level}: must be a multiple of 0.5 (e.g. 1.0, 1.5, 2.0)."
        )
    if level % 1 == 0:
        return CPM[int(level) - 1]
    cpmPrevd, cpmNextd = get_cpm(level - 0.5), get_cpm(level + 0.5)
    return f32(((cpmPrevd**2 + cpmNextd**2) / 2) ** 0.5)


def get_rcpm(level: int) -> float:
    return RCPM[level - 1]


def get_stats(
    poke: PokemonSettings, cpm: float, iv_atk: int, iv_def: int, iv_sta: int
) -> tuple[float, float, float]:
    atk_stat = (poke.stats.base_attack + iv_atk) * cpm
    def_stat = (poke.stats.base_defense + iv_def) * cpm
    sta_stat = (poke.stats.base_stamina + iv_sta) * cpm
    return atk_stat, def_stat, sta_stat


def get_tgr_stats(
    poke: PokemonSettings,
    cpm: float,
    rank: HoloCharacterCategory,
    iv_atk: int,
    iv_def: int,
    iv_sta: int,
) -> tuple[float, float, float]:
    rank_mult = get_tgr_rank_mult(rank)
    atk_stat = floor((poke.stats.base_attack + iv_atk) * 5 / 3) * cpm * rank_mult
    def_stat = (poke.stats.base_defense + iv_def) * cpm * rank_mult
    sta_stat = floor((poke.stats.base_stamina + iv_sta) * 3 / 5) * cpm * rank_mult
    return atk_stat, def_stat, sta_stat


def get_cp(
    poke: PokemonSettings, cpm: float, iv_atk: int, iv_def: int, iv_sta: int
) -> int:
    return _get_cp(*get_stats(poke, cpm, iv_atk, iv_def, iv_sta))


def get_hp(poke: PokemonSettings, cpm: float, iv_sta: int) -> int:
    _, _, sta_stat = get_stats(poke, cpm, 0, 0, iv_sta)
    return _get_hp(sta_stat)


def get_tgr_cp(
    poke: PokemonSettings,
    cpm: float,
    rank: HoloCharacterCategory,
    iv_atk: int,
    iv_def: int,
    iv_sta: int,
) -> int:
    return _get_cp(*get_tgr_stats(poke, cpm, rank, iv_atk, iv_def, iv_sta))


def get_tgr_hp(
    poke: PokemonSettings, cpm: float, rank: HoloCharacterCategory, iv_sta: int
) -> int:
    _, _, sta_stat = get_tgr_stats(poke, cpm, rank, 0, 0, iv_sta)
    return _get_hp(sta_stat)


def _get_cp(atk_stat: float, def_stat: float, sta_stat: float) -> int:
    return max(10, floor(atk_stat * (def_stat * sta_stat) ** 0.5 * 0.1))


def _get_hp(sta_stat: float) -> int:
    return max(10, floor(sta_stat))
