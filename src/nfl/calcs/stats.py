from math import floor

from nfl.data import CPM, RCPM, PokeSpecies, get_pokemon_settings, get_tgr_rank_mult
from nfl.exceptions import ValidationError
from nfl.proto import HoloCharacterCategory, PokemonSettings
from nfl.utils import f32


def get_cpm(level: float) -> float:
    if level % 0.5 != 0:
        raise ValidationError(
            f"Invalid level {level}: must be a multiple of 0.5 (e.g. 1.0, 1.5, 2.0)."
        )
    if not 1.0 <= level <= len(CPM):
        raise ValidationError(
            f"Invalid level {level}: must be between 1.0 and {len(CPM):.1f}."
        )
    if level % 1 == 0:
        return CPM[int(level) - 1]
    cpm_prev = get_cpm(level - 0.5)
    cpm_next = get_cpm(level + 0.5)
    return f32(((cpm_prev**2 + cpm_next**2) / 2) ** 0.5)


def get_rcpm(level: int) -> float:
    if not 1 <= level <= len(RCPM):
        raise ValidationError(
            f"Invalid level {level}: must be between 1 and {len(RCPM)}."
        )
    return RCPM[level - 1]


def get_stats(
    poke: PokeSpecies, level: float, iv_atk: int, iv_def: int, iv_sta: int
) -> tuple[float, float, float]:
    poke_sett = get_pokemon_settings(poke)
    cpm = get_cpm(level)
    return get_stats_raw(poke_sett, cpm, iv_atk, iv_def, iv_sta)


def get_stats_raw(
    poke_sett: PokemonSettings, cpm: float, iv_atk: int, iv_def: int, iv_sta: int
) -> tuple[float, float, float]:
    atk_stat = (poke_sett.stats.base_attack + iv_atk) * cpm
    def_stat = (poke_sett.stats.base_defense + iv_def) * cpm
    sta_stat = (poke_sett.stats.base_stamina + iv_sta) * cpm
    return atk_stat, def_stat, sta_stat


def get_tgr_stats(
    poke: PokeSpecies,
    level: int,
    rank: HoloCharacterCategory,
    iv_atk: int,
    iv_def: int,
    iv_sta: int,
) -> tuple[float, float, float]:
    poke_sett = get_pokemon_settings(poke)
    rcpm = get_rcpm(level)
    return get_tgr_stats_raw(poke_sett, rcpm, rank, iv_atk, iv_def, iv_sta)


def get_tgr_stats_raw(
    poke_sett: PokemonSettings,
    rcpm: float,
    rank: HoloCharacterCategory,
    iv_atk: int,
    iv_def: int,
    iv_sta: int,
) -> tuple[float, float, float]:
    rank_mult = get_tgr_rank_mult(rank)
    atk_stat = floor((poke_sett.stats.base_attack + iv_atk) * 5 / 3) * rcpm * rank_mult
    def_stat = (poke_sett.stats.base_defense + iv_def) * rcpm * rank_mult
    sta_stat = floor((poke_sett.stats.base_stamina + iv_sta) * 3 / 5) * rcpm * rank_mult
    return atk_stat, def_stat, sta_stat


def get_cp(
    poke: PokeSpecies, level: float, iv_atk: int, iv_def: int, iv_sta: int
) -> int:
    return _get_cp(*get_stats(poke, level, iv_atk, iv_def, iv_sta))


def get_cp_raw(
    poke_sett: PokemonSettings, cpm: float, iv_atk: int, iv_def: int, iv_sta: int
) -> int:
    return _get_cp(*get_stats_raw(poke_sett, cpm, iv_atk, iv_def, iv_sta))


def get_hp(poke: PokeSpecies, level: float, iv_sta: int) -> int:
    _, _, sta_stat = get_stats(poke, level, 0, 0, iv_sta)
    return _get_hp(sta_stat)


def get_hp_raw(poke_sett: PokemonSettings, cpm: float, iv_sta: int) -> int:
    _, _, sta_stat = get_stats_raw(poke_sett, cpm, 0, 0, iv_sta)
    return _get_hp(sta_stat)


def get_tgr_cp(
    poke: PokeSpecies,
    level: int,
    rank: HoloCharacterCategory,
    iv_atk: int,
    iv_def: int,
    iv_sta: int,
) -> int:
    return _get_cp(*get_tgr_stats(poke, level, rank, iv_atk, iv_def, iv_sta))


def get_tgr_cp_raw(
    poke_sett: PokemonSettings,
    rcpm: float,
    rank: HoloCharacterCategory,
    iv_atk: int,
    iv_def: int,
    iv_sta: int,
) -> int:
    return _get_cp(*get_tgr_stats_raw(poke_sett, rcpm, rank, iv_atk, iv_def, iv_sta))


def get_tgr_hp(
    poke: PokeSpecies, level: int, rank: HoloCharacterCategory, iv_sta: int
) -> int:
    _, _, sta_stat = get_tgr_stats(poke, level, rank, 0, 0, iv_sta)
    return _get_hp(sta_stat)


def get_tgr_hp_raw(
    poke_sett: PokemonSettings, rcpm: float, rank: HoloCharacterCategory, iv_sta: int
) -> int:
    _, _, sta_stat = get_tgr_stats_raw(poke_sett, rcpm, rank, 0, 0, iv_sta)
    return _get_hp(sta_stat)


def _get_cp(atk_stat: float, def_stat: float, sta_stat: float) -> int:
    return max(10, floor(atk_stat * (def_stat * sta_stat) ** 0.5 * 0.1))


def _get_hp(sta_stat: float) -> int:
    return max(10, floor(sta_stat))
