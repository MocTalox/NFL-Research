from collections.abc import Callable
from functools import partial
from itertools import count
from math import floor

from nfl.calcs import (
    BattlePokemon,
    BattleState,
    damage_formula_raw,
    get_cpm,
    get_hp,
)
from nfl.calcs.damage import get_effect
from nfl.data import (
    POKEMON,
    PVE_MOVES,
    PokeSpecies,
    get_move_boosting_weather,
)
from nfl.proto import (
    HoloAlignment,
    HoloCombatType,
    HoloPokemonMove,
    HoloWeatherCondition,
)
from nfl.utils import f32, f32_step, f64


def get_cpm_list(levels: list[float]) -> list[tuple[float, float]]:
    return [(level, get_cpm(level)) for level in levels]


dialga = POKEMON.get(PokeSpecies.resolve("dialga"))
assert dialga
boss = BattlePokemon(
    dialga,
    15,
    15,
    15,
    f32(0.82),
    HoloAlignment.SHADOW,
)
boss_moves = [
    *dialga.quick_moves,
    *dialga.elite_quick_move,
    *dialga.cinematic_moves,
    *dialga.elite_cinematic_move,
]

defenders = [
    POKEMON.get(ps)
    for ps in [
        PokeSpecies.resolve("Bulbasaur"),
        PokeSpecies.resolve("Ivysaur"),
        PokeSpecies.resolve("Venusaur"),
        PokeSpecies.resolve("Raichu", "Alola"),
        PokeSpecies.resolve("Drowzee"),
        PokeSpecies.resolve("Hypno"),
        PokeSpecies.resolve("Jolteon"),
        PokeSpecies.resolve("Dratini"),
        PokeSpecies.resolve("Dragonair"),
        PokeSpecies.resolve("Dragonite"),
        PokeSpecies.resolve("Houndour"),
        PokeSpecies.resolve("Houndoom"),
        PokeSpecies.resolve("Lileep"),
        PokeSpecies.resolve("Cradily"),
        PokeSpecies.resolve("Combee"),
    ]
]
defenders = [poke for s in POKEMON.values() for poke in s]


def raw_dmg_func(
    move: HoloPokemonMove, state: BattleState, defender: BattlePokemon, mult: float
):
    move_settings = PVE_MOVES[move]
    return mult * damage_formula_raw(
        boss, defender, move_settings.power, move_settings.pokemon_type, 0, False, state
    )


"""
def test_dmg_func(
    move: HoloPokemonMove,
    weather_id: HoloWeatherCondition,
    defender_ps: PokeSpecies,
    level: float,
    iv_def: int
):
    state = BattleState()
    state.weather_id = weather_id
    defender = BattlePokemon()
    defender.pokemon_settings = get_poke_settings(defender_ps)
    defender.def_iv = iv_def
    defender.cpm = get_cpm(level)
    low, hig = f32_step(1.7989907554974764, -10), f32_step(1.7989907554974764, 10)
    return raw_dmg_func(low, move, state, defender), raw_dmg_func(hig, move, state, defender)

print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("CHARIZARD"), 19.5, 10))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SLOWKING"), 16.0, 13))
print("Lv5.5 NFL 7")
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("FLAAFFY"), 5.5,  2))
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("FUECOCO"), 5.5,  6))
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("WAILMER"), 5.5,  6))
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("JOLTIK"), 5.5, 13))
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("PIKACHU"), 5.5, 15))
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("BLASTOISE"), 5.5, 15))
print("Lv16.0 NFL 3")
print(test_dmg_func("DRAGON_BREATH_FAST", None, PokeSpecies.resolve("NINETALES", "NINETALES_ALOLA"), 16.0,  0))
print(test_dmg_func("DRAGON_BREATH_FAST", None, PokeSpecies.resolve("TOGETIC"), 16.0, 12))
print("Lv34.5 NFL 3")
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("NINETALES", "NINETALES_ALOLA"), 34.5,  2))
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("COBALION"), 34.5, 15))

exit(0)

"""
"""
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("COBALION"), 34.5, 15))
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("HATTERENE"), 34.5, 13))
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("GARDEVOIR"), 34.5,  0))
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("NINETALES", "NINETALES_ALOLA"), 34.5,  2))
print(test_dmg_func("DRACO_METEOR", None, PokeSpecies.resolve("PRIMARINA"), 34.5,  0))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("TOGEDEMARU"), 34.5, 11))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("MAGNEMITE"), 34.5,  1))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("MAGNETON"), 34.5, 14))

print(test_dmg_func("DRAGON_BREATH_FAST", None, PokeSpecies.resolve("HATTERENE"), 16.0, 11))
print(test_dmg_func("DRAGON_BREATH_FAST", None, PokeSpecies.resolve("TOGETIC"), 16.0, 12))
print(test_dmg_func("DRAGON_BREATH_FAST", None, PokeSpecies.resolve("NINETALES", "NINETALES_ALOLA"), 16.0,  0))
print(test_dmg_func("METAL_CLAW_FAST", None, PokeSpecies.resolve("EMPOLEON"), 16.0,  7))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("POLIWRATH"), 16.0,  9))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SLOWKING"), 16.0, 13))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("EMPOLEON"), 16.0,  7))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("JELLICENT"), 16.0, 15))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SLOWBRO"), 16.0, 13))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("GYARADOS"), 16.0,  7))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SKELEDIRGE"), 16.0, 15))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("CORVIKNIGHT"), 16.0,  1))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("MELMETAL"), 16.0,  3))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("POLITOED"), 16.0, 14))

print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SLOWKING"), 19.5,  3))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("TYPHLOSION", "TYPHLOSION_HISUIAN"), 19.5, 11))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("TYPHLOSION"), 19.5, 10))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("JELLICENT"), 19.5,  5))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("LUDICOLO"), 19.5,  7))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SLOWBRO"), 19.5,  3))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("LUMINEON"), 19.5, 13))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SCIZOR"), 19.5,  2))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("MAGMORTAR"), 19.5, 11))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SKELEDIRGE"), 19.5,  5))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("INCINEROAR"), 19.5,  8))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("STUNFISK"), 19.5, 12))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("STUNFISK", "STUNFISK_GALARIAN"), 19.5, 12))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("CHARIZARD"), 19.5, 10))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("AMPHAROS"), 19.5, 14))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("SWAMPERT"), 19.5,  8))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("POLITOED"), 19.5,  4))
print(test_dmg_func("IRON_HEAD", None, PokeSpecies.resolve("CLAWITZER"), 19.5, 12))

exit(0)
"""


def cpm_floats_diff(
    dmg_func: Callable[[float], float], base: float, a: float, b: float
):
    base_value = floor(dmg_func(base))
    step = floor(dmg_func(a)) + floor(dmg_func(b)) - 2 * base_value
    if step == 0:
        raise ValueError(
            f"Cannot calculate CPM float difference: no change detected for "
            f"base={base}, a={a}, b={b}"
        )
    return next(
        n - step
        for n in count(step, step)
        if base_value != floor(dmg_func(f32_step(base, n)))
    )


res: list[list[object]] = []
state = BattleState(HoloCombatType.COMBAT_TYPE_RAID)
defender = BattlePokemon()
base, low, hig = 1.7989907554974764, 1.79898, 1.799
low, hig = f32_step(base, -25), f32_step(base, 25)
print("Starting")
for move in boss_moves:
    for state.weather_id in (
        HoloWeatherCondition.NONE,
        get_move_boosting_weather(move),
    ):
        print(f"## Moveset: {state.weather_id} {move}")
        for defender.pokemon_settings in defenders:
            for level, defender.cpm in get_cpm_list(
                [(n + 1) / 2 for n in range(1, 70)]
            ):
                for defender.def_iv in range(16):
                    dmg_func = partial(raw_dmg_func, move, state, defender)
                    raw_dmg_low = dmg_func(low)
                    raw_dmg_hig = dmg_func(hig)
                    if floor(raw_dmg_low) != floor(raw_dmg_hig):
                        max_dmg = floor(raw_dmg_hig) + 1
                        hp_func = partial(
                            get_hp, defender.pokemon_settings, defender.cpm
                        )
                        min_iv_sta = next(
                            (sta for sta in range(16) if hp_func(sta) > max_dmg), None
                        )
                        if min_iv_sta is not None:
                            dmg = dmg_func(base)
                            bulk = (
                                defender.pokemon_settings.stats.base_defense
                                + defender.def_iv
                            )
                            eff = get_effect(
                                PVE_MOVES[move].pokemon_type,
                                defender.pokemon_settings.type,
                                defender.pokemon_settings.type_2,
                            )
                            res.append(
                                [
                                    move,
                                    state.weather_id,
                                    defender.pokemon_settings.pokemon_id,
                                    defender.pokemon_settings.form,
                                    level,
                                    defender.def_iv,
                                    min_iv_sta,
                                    cpm_floats_diff(dmg_func, base, low, hig),
                                    f64(round(dmg) * bulk / f64(eff)),
                                    f64(f32(dmg)),
                                ]
                            )
print("Finished")

res.sort(key=lambda d: (d[4], d[8]))


def run():
    return res
