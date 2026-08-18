from nfl.helpers import PokeSpecies
from nfl.proto import HoloTempEvoId
from nfl.service.common.data import (
    get_pokemon_extended_settings,
    get_pokemon_settings,
    get_temp_evo_pokemon_settings,
    get_temp_evo_size_settings,
)
from nfl.service.common.size_class import SizeClass
from nfl.service.logic.contest_score import Pokemon, contest_score


def poke(
    name: str,
    form: str | None,
    temp_evo_id: HoloTempEvoId = HoloTempEvoId.TEMP_EVOLUTION_UNSET,
):
    poke = PokeSpecies.resolve(name, form)
    pokemon_settings = get_pokemon_settings(poke)
    extended_settings = get_pokemon_extended_settings(poke)
    assert pokemon_settings and extended_settings
    if temp_evo_id:
        pokemon_settings = get_temp_evo_pokemon_settings(pokemon_settings, temp_evo_id)
        size_settings = get_temp_evo_size_settings(extended_settings, temp_evo_id)
    else:
        size_settings = extended_settings.size_settings
    return (pokemon_settings, size_settings)


def run():
    print(
        contest_score(
            Pokemon(
                *poke("FALINKS", None, HoloTempEvoId.TEMP_EVOLUTION_MEGA),
                100,
                750.63,
                4.57,
                SizeClass.XXL,
            )
        )
    )
    print(
        contest_score(
            Pokemon(
                *poke("PUMPKABOO", "PUMPKABOO_SMALL"),
                1 + 14 + 13,
                6.245460033416748,
                0.38999998569488525,
                SizeClass.XS,
            )
        )
    )
    print(
        contest_score(
            Pokemon(
                *poke("LECHONK", None),
                15 + 5 + 14,
                12.45292664,
                0.7535949945,
                SizeClass.XXL,
            )
        )
    )  # 1083.063422
    print(
        contest_score(
            Pokemon(
                *poke("BUNNELBY", None),
                6 + 3 + 12,
                7.73238802,
                0.644746244,
                SizeClass.XXL,
            )
        )
    )  # 1041.333484
    print(
        contest_score(
            Pokemon(
                *poke("SLAKOTH", None),
                5 + 15 + 9,
                40.85430145,
                1.269156933,
                SizeClass.XXL,
            )
        )
    )  # 1058.167837
    print(
        contest_score(
            Pokemon(
                *poke("SWABLU", None),
                12 + 9 + 13,
                1.874579191,
                0.6359647512,
                SizeClass.XXL,
            )
        )
    )  # 1029.059482
    print(
        contest_score(
            Pokemon(
                *poke("LECHONK", None),
                14 + 10 + 15,
                25.04260826,
                0.7472822666,
                SizeClass.XL,
            )
        )
    )  # 994.3671879
    print(
        contest_score(
            Pokemon(
                *poke("FLETCHLING", None),
                14 + 10 + 15,
                3.760264158,
                0.4429859519,
                SizeClass.XL,
            )
        )
    )  # 865.8209233
    print(
        contest_score(
            Pokemon(
                *poke("EEVEE", None),
                12 + 14 + 12,
                13.47558212,
                0.4332978427,
                SizeClass.XL,
            )
        )
    )  # 840.6967393
    print(
        contest_score(
            Pokemon(
                *poke("MEOWTH", None),
                12 + 10 + 1,
                8.567674637,
                0.5929412842,
                SizeClass.XL,
            )
        )
    )  # 839.197601
    print(
        contest_score(
            Pokemon(
                *poke("GREEDENT", None),
                15 + 4 + 13,
                12.92473984,
                0.8630484343,
                SizeClass.XL,
            )
        )
    )  # 836.7245278
    print(
        contest_score(
            Pokemon(
                *poke("BUNNELBY", None),
                10 + 10 + 10,
                9.343919754,
                0.5874073505,
                SizeClass.XL,
            )
        )
    )  # 829.2416278
    print(
        contest_score(
            Pokemon(
                *poke("WOOLOO", None),
                13 + 10 + 14,
                12.15228081,
                0.8264663815,
                SizeClass.XL,
            )
        )
    )  # 805.8251632
    print(
        contest_score(
            Pokemon(
                *poke("BRAVIARY", None),
                14 + 15 + 15,
                82.33031464,
                1.985008478,
                SizeClass.XL,
            )
        )
    )  # 787.714284
    print(
        contest_score(
            Pokemon(
                *poke("FURFROU", None),
                4 + 10 + 13,
                41.74080658,
                1.392283916,
                SizeClass.M,
            )
        )
    )  # 737.9105546
    print(
        contest_score(
            Pokemon(
                *poke("ZIGZAGOON", None),
                14 + 15 + 14,
                29.18685532,
                0.4736663401,
                SizeClass.M,
            )
        )
    )  # 700.2987674
    print(
        contest_score(
            Pokemon(
                *poke("SPINDA", None),
                15 + 15 + 14,
                6.162862301,
                1.19097209,
                SizeClass.M,
            )
        )
    )  # 703.0177429
    print(
        contest_score(
            Pokemon(
                *poke("TOUCANNON", None),
                15 + 15 + 13,
                41.21990585,
                1.399943352,
                SizeClass.XL,
            )
        )
    )  # 735.2645051
    print(
        contest_score(
            Pokemon(
                *poke("REGIGIGAS", None),
                10 + 13 + 12,
                414.9747314,
                3.983692408,
                SizeClass.M,
            )
        )
    )  # 666.8866408
    print(
        contest_score(
            Pokemon(
                *poke("REGIGIGAS", None),
                13 + 13 + 14,
                511.1306152,
                3.960818291,
                SizeClass.M,
            )
        )
    )  # 686.0032829
    print(
        contest_score(
            Pokemon(
                *poke("LICKITUNG", None),
                5 + 12 + 13,
                139.0036011,
                1.707127094,
                SizeClass.XL,
            )
        )
    )  # 825.1469862
    print(
        contest_score(
            Pokemon(
                *poke("DUDUNSPARCE", None),
                3 + 15 + 3,
                68.77416992,
                4.494625092,
                SizeClass.M,
            )
        )
    )  # 796.0979214
    print(
        contest_score(
            Pokemon(
                *poke("KECLEON", None),
                2 + 11 + 3,
                30.15408516,
                1.127774239,
                SizeClass.M,
            )
        )
    )  # 706.0251212
    print(
        contest_score(
            Pokemon(
                *poke("SNORLAX", None),
                9 + 13 + 8,
                832.1674194,
                2.756881475,
                SizeClass.XL,
            )
        )
    )  # 754.074779
    print(
        contest_score(
            Pokemon(
                *poke("SAWSBUCK", None),
                5 + 13 + 4,
                123.8382339,
                2.141122341,
                SizeClass.M,
            )
        )
    )  # 704.0339862
    print(
        contest_score(
            Pokemon(
                *poke("SLAKING", None),
                15 + 11 + 15,
                148.1611633,
                2.168533564,
                SizeClass.M,
            )
        )
    )  # 685.4662024
    print(
        contest_score(
            Pokemon(
                *poke("WEEZING", None),
                5 + 12 + 5,
                33.9213028,
                4.43392849,
                SizeClass.XL,
            )
        )
    )  # 1716.660356
    print(
        contest_score(
            Pokemon(
                *poke("WEEZING", None),
                13 + 15 + 15,
                15.5542469,
                2.966056585,
                SizeClass.M,
            )
        )
    )  # 1134.700616
    print(
        contest_score(
            Pokemon(
                *poke("KOFFING", None),
                2 + 13 + 14,
                1.944025517,
                1.140901327,
                SizeClass.XXL,
            )
        )
    )  # 1087.513388
    print(
        contest_score(
            Pokemon(
                *poke("FOONGUS", None),
                14 + 1 + 12,
                1.593192816,
                0.3040541112,
                SizeClass.XXL,
            )
        )
    )  # 911.7485629
    print(
        contest_score(
            Pokemon(
                *poke("CLODSIRE", None),
                1 + 10 + 9,
                338.25177,
                2.237792969,
                SizeClass.M,
            )
        )
    )  # 774.8704192
    print(
        contest_score(
            Pokemon(
                *poke("BELLSPROUT", None),
                10 + 13 + 14,
                6.450083733,
                0.8644111156,
                SizeClass.M,
            )
        )
    )  # 796.4542323
    print(
        contest_score(
            Pokemon(
                *poke("TOXEL", None),
                12 + 14 + 13,
                17.39114571,
                0.472276926,
                SizeClass.M,
            )
        )
    )  # 688.4792839
    print(
        contest_score(
            Pokemon(
                *poke("GASTLY", None),
                7 + 14 + 5,
                0.2158249617,
                1.838631988,
                SizeClass.XL,
            )
        )
    )  # 724.1168059
    print(
        contest_score(
            Pokemon(
                *poke("ROSERADE", None),
                1 + 12 + 11,
                26.10993576,
                1.205184102,
                SizeClass.XL,
            )
        )
    )  # 758.869334
    print(
        contest_score(
            Pokemon(
                *poke("SALANDIT", None),
                10 + 10 + 10,
                6.653783321,
                0.7415748239,
                SizeClass.M,
            )
        )
    )  # 690.7564124
