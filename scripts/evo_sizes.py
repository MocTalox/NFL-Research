from typing import Any

from nfl.calcs import SizedPokemon, evolution_size_range
from nfl.data import PokeSpecies, SizeClass
from nfl.proto import HoloTempEvoId


def _format_value(min_val: str, max_val: str) -> str:
    if min_val == max_val:
        return min_val
    return f"{min_val}-{max_val}"


def print_size(values: dict[str, Any], decimals: int = 2):
    weight_min = f"{values['weight']['min']:.{decimals}f}"
    weight_max = f"{values['weight']['max']:.{decimals}f}"
    height_min = f"{values['height']['min']:.{decimals}f}"
    height_max = f"{values['height']['max']:.{decimals}f}"
    size_class_min = str(values["size_class"]["min"])
    size_class_max = str(values["size_class"]["max"])
    print(
        f"Weight: {_format_value(weight_min, weight_max)}kg, "
        f"Height: {_format_value(height_min, height_max)}m, "
        f"Size Class: {_format_value(size_class_min, size_class_max)}"
    )


def run():
    print("# Normal Evolutions")
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("TEDDIURSA"), 20.71, 0.93, SizeClass.XXL
            ),
            PokeSpecies.resolve("URSARING"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("TEDDIURSA"), 20.71, 0.93, SizeClass.XXL
            ),
            PokeSpecies.resolve("URSALUNA"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("ZORUA"), 4000.0, 0.6, SizeClass.M),
            PokeSpecies.resolve("ZOROARK"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("ZORUA"), 4000.0, 1.2, SizeClass.XXL
            ),
            PokeSpecies.resolve("ZOROARK"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("PUMPKABOO", "PUMPKABOO_SUPER"),
                17.5,
                0.75,
                SizeClass.XXL,
            ),
            PokeSpecies.resolve("GOURGEIST", "GOURGEIST_SUPER"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("PUMPKABOO", "PUMPKABOO_AVERAGE"),
                6.3,
                0.42,
                SizeClass.M,
            ),
            PokeSpecies.resolve("GOURGEIST", "GOURGEIST_AVERAGE"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("CUBCHOO"), 1.93, 0.25, SizeClass.XXS
            ),
            PokeSpecies.resolve("BEARTIC"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("PUMPKABOO", "PUMPKABOO_SUPER"),
                18.29,
                0.75,
                SizeClass.XXL,
            ),
            PokeSpecies.resolve("GOURGEIST", "GOURGEIST_SUPER"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("KYUREM"), 403.21, 3.45, SizeClass.M
            ),
            PokeSpecies.resolve("KYUREM", "KYUREM_WHITE"),
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("KYUREM"), 405.1, 3.22, SizeClass.M),
            PokeSpecies.resolve("KYUREM", "KYUREM_BLACK"),
        )
    )

    print("# Mega Evolutions")
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("METAGROSS"), 979.35, 2.02, SizeClass.XL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("PIDGEOT"), 68.48, 2.52, SizeClass.XXL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("FALINKS"), 7.37, 1.48, SizeClass.XXS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("SCEPTILE"), 48.17, 1.64, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("VENUSAUR"), 48.65, 1.51, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("CAMERUPT"), 216.79, 1.94, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("SLOWBRO"), 42.96, 1.23, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("MAWILE"), 15.04, 0.66, SizeClass.M),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("AUDINO"), 19.04, 0.85, SizeClass.M),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("SHARPEDO"), 103.72, 1.76, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("ABSOL"), 53.63, 1.33, SizeClass.M),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("HERACROSS"), 68.49, 1.64, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("HERACROSS"), 78.89, 1.83, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("AMPHAROS"), 62.69, 1.35, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("GALLADE"), 63.47, 1.89, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("LATIOS"), 53.79, 2.03, SizeClass.M),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("LATIOS"), 77.63, 2.27, SizeClass.M),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("GARCHOMP"), 123.46, 2.07, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("GARCHOMP"), 87.26, 1.9, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("SALAMENCE"), 112.23, 1.71, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("FALINKS"), 45.28, 2.62, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(PokeSpecies.resolve("PINSIR"), 71.89, 1.68, SizeClass.M),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("ABOMASNOW"), 22.54, 1.09, SizeClass.XXS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 19.45, 1.09
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("LATIAS"), 12.13, 0.7, SizeClass.XXS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 10.0, 0.
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("LATIOS"), 14.28, 0.99, SizeClass.XXS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 12.68, 0.99
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("STEELIX"), 164.34, 6.63, SizeClass.XS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 251.17, 6.63
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("BEEDRILL"), 13.3, 0.68, SizeClass.XS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 9.26, 0.68
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("SWAMPERT"), 49.27, 0.98, SizeClass.XS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 41.51, 0.98
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("FALINKS"), 87.72, 4.57, SizeClass.XXL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 750.63, 4.57
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("VENUSAUR"), 181.58, 3.35, SizeClass.XXL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 267.94, 3.68
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("PIDGEOT"), 71.34, 2.04, SizeClass.XL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 63.99, 2.51
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("ALAKAZAM"), 83.69, 2.5, SizeClass.XXL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
        )
    )  # 63.12, 1.84
    # https://www.threads.com/@cody_02_27/post/DZXottzk1yo
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("MEWTWO"), 191.56, 3.14, SizeClass.XXL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_X,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("MEWTWO"), 191.56, 3.14, SizeClass.XXL
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_Y,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("KYOGRE"), 143.15, 3.44, SizeClass.M
            ),
            HoloTempEvoId.TEMP_EVOLUTION_PRIMAL,
        )
    )  # 430.0, 3.44
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("MEWTWO"), 30.19, 0.99, SizeClass.XXS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_X,
        )
    )
    print_size(
        evolution_size_range(
            SizedPokemon.build(
                PokeSpecies.resolve("MEWTWO"), 30.19, 0.99, SizeClass.XXS
            ),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_Y,
        )
    )
