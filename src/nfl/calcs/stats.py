from math import floor

from nfl.data import CPM, RCPM, PokeSpecies, get_pokemon_settings, get_tgr_rank_mult
from nfl.exceptions import ValidationError
from nfl.proto import HoloCharacterCategory, PokemonSettings
from nfl.utils import f32


def get_cpm(level: float) -> float:
    if level % 0.5 != 0:
        raise ValidationError("INVALID_LEVEL_DECIMALS", level=level)
    if not 1.0 <= level <= len(CPM):
        raise ValidationError("INVALID_LEVEL_RANGE", level=level, max_level=len(CPM))
    if level % 1 == 0:
        return CPM[int(level) - 1]
    cpm_prev = get_cpm(level - 0.5)
    cpm_next = get_cpm(level + 0.5)
    return f32(((cpm_prev**2 + cpm_next**2) / 2) ** 0.5)


def get_rcpm(level: int) -> float:
    if not 1 <= level <= len(RCPM):
        raise ValidationError(
            "INVALID_LEVEL_RANGE_TGR", level=level, max_level=len(RCPM)
        )
    return RCPM[level - 1]


def get_stats(
    poke: PokeSpecies | None = None,
    poke_sett: PokemonSettings | None = None,
    base_atk: int | None = None,
    base_def: int | None = None,
    base_sta: int | None = None,
    level: float | None = None,
    cpm: float | None = None,
    iv_atk: int = 15,
    iv_def: int = 15,
    iv_sta: int = 15,
) -> tuple[float, float, float]:
    if poke is not None:
        poke_sett = get_pokemon_settings(poke)
    if poke_sett is not None:
        base_atk = poke_sett.stats.base_attack
        base_def = poke_sett.stats.base_defense
        base_sta = poke_sett.stats.base_stamina
    if base_atk is None or base_def is None or base_sta is None:
        raise ValidationError("")  # TODO Add error code

    if level is not None:
        cpm = get_cpm(level)
    if cpm is None:
        raise ValidationError("")  # TODO Add error code

    atk_stat = (base_atk + iv_atk) * cpm
    def_stat = (base_def + iv_def) * cpm
    sta_stat = (base_sta + iv_sta) * cpm

    return atk_stat, def_stat, sta_stat


def get_tgr_stats(
    poke: PokeSpecies | None = None,
    poke_sett: PokemonSettings | None = None,
    base_atk: int | None = None,
    base_def: int | None = None,
    base_sta: int | None = None,
    level: int | None = None,
    rcpm: float | None = None,
    enemy: HoloCharacterCategory | None = None,
    rank_mult: float | None = None,
    iv_atk: int = 15,
    iv_def: int = 15,
    iv_sta: int = 15,
) -> tuple[float, float, float]:
    if poke is not None:
        poke_sett = get_pokemon_settings(poke)
    if poke_sett is not None:
        base_atk = poke_sett.stats.base_attack
        base_def = poke_sett.stats.base_defense
        base_sta = poke_sett.stats.base_stamina
    if base_atk is None or base_def is None or base_sta is None:
        raise ValidationError("")  # TODO Add error code

    if level is not None:
        rcpm = get_rcpm(level)
    if rcpm is None:
        raise ValidationError("")  # TODO Add error code

    if enemy is not None:
        rank_mult = get_tgr_rank_mult(enemy)
    if rank_mult is None:
        raise ValidationError("")  # TODO Add error code

    atk_stat = floor((base_atk + iv_atk) * 5 / 3) * rcpm * rank_mult
    def_stat = (base_def + iv_def) * rcpm * rank_mult
    sta_stat = floor((base_sta + iv_sta) * 3 / 5) * rcpm * rank_mult

    return atk_stat, def_stat, sta_stat


def get_cp(
    poke: PokeSpecies | None = None,
    poke_sett: PokemonSettings | None = None,
    base_atk: int | None = None,
    base_def: int | None = None,
    base_sta: int | None = None,
    level: float | None = None,
    cpm: float | None = None,
    iv_atk: int = 15,
    iv_def: int = 15,
    iv_sta: int = 15,
) -> int:
    atk_stat, def_stat, sta_stat = get_stats(
        poke,
        poke_sett,
        base_atk,
        base_def,
        base_sta,
        level,
        cpm,
        iv_atk,
        iv_def,
        iv_sta,
    )

    return _get_cp(atk_stat, def_stat, sta_stat)


def get_hp(
    poke: PokeSpecies | None = None,
    poke_sett: PokemonSettings | None = None,
    base_sta: int | None = None,
    level: float | None = None,
    cpm: float | None = None,
    iv_sta: int = 15,
) -> int:
    _, _, sta_stat = get_stats(
        poke,
        poke_sett,
        0,
        0,
        base_sta,
        level,
        cpm,
        0,
        0,
        iv_sta,
    )

    return _get_hp(sta_stat)


def get_tgr_cp(
    poke: PokeSpecies | None = None,
    poke_sett: PokemonSettings | None = None,
    base_atk: int | None = None,
    base_def: int | None = None,
    base_sta: int | None = None,
    level: int | None = None,
    rcpm: float | None = None,
    enemy: HoloCharacterCategory | None = None,
    rank_mult: float | None = None,
    iv_atk: int = 15,
    iv_def: int = 15,
    iv_sta: int = 15,
) -> int:
    atk_stat, def_stat, sta_stat = get_tgr_stats(
        poke,
        poke_sett,
        base_atk,
        base_def,
        base_sta,
        level,
        rcpm,
        enemy,
        rank_mult,
        iv_atk,
        iv_def,
        iv_sta,
    )

    return _get_cp(atk_stat, def_stat, sta_stat)


def get_tgr_hp(
    poke: PokeSpecies | None = None,
    poke_sett: PokemonSettings | None = None,
    base_sta: int | None = None,
    level: int | None = None,
    rcpm: float | None = None,
    enemy: HoloCharacterCategory | None = None,
    rank_mult: float | None = None,
    iv_sta: int = 15,
) -> int:
    _, _, sta_stat = get_tgr_stats(
        poke,
        poke_sett,
        0,
        0,
        base_sta,
        level,
        rcpm,
        enemy,
        rank_mult,
        0,
        0,
        iv_sta,
    )

    return _get_hp(sta_stat)


def _get_cp(atk_stat: float, def_stat: float, sta_stat: float) -> int:
    return max(10, floor(atk_stat * (def_stat * sta_stat) ** 0.5 * 0.1))


def _get_hp(sta_stat: float) -> int:
    return max(10, floor(sta_stat))
