from typing import Any

from nfl.calcs import evolution_size_range
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
            PokeSpecies.resolve("TEDDIURSA"),
            PokeSpecies.resolve("URSARING"),
            20.71,
            0.93,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("TEDDIURSA"),
            PokeSpecies.resolve("URSALUNA"),
            20.71,
            0.93,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("ZORUA"),
            PokeSpecies.resolve("ZOROARK"),
            4000.0,
            0.6,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("ZORUA"),
            PokeSpecies.resolve("ZOROARK"),
            4000.0,
            1.2,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("PUMPKABOO", "PUMPKABOO_SUPER"),
            PokeSpecies.resolve("GOURGEIST", "GOURGEIST_SUPER"),
            17.5,
            0.75,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("PUMPKABOO", "PUMPKABOO_AVERAGE"),
            PokeSpecies.resolve("GOURGEIST", "GOURGEIST_AVERAGE"),
            6.3,
            0.42,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("CUBCHOO"),
            PokeSpecies.resolve("BEARTIC"),
            1.93,
            0.25,
            SizeClass.XXS,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("PUMPKABOO", "PUMPKABOO_SUPER"),
            PokeSpecies.resolve("GOURGEIST", "GOURGEIST_SUPER"),
            18.29,
            0.75,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("KYUREM"),
            PokeSpecies.resolve("KYUREM", "KYUREM_WHITE"),
            403.21,
            3.45,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("KYUREM"),
            PokeSpecies.resolve("KYUREM", "KYUREM_BLACK"),
            405.1,
            3.22,
            SizeClass.M,
        )
    )

    print("# Mega Evolutions")
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("METAGROSS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            979.35,
            2.02,
            SizeClass.XL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("PIDGEOT"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            68.48,
            2.52,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("FALINKS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            7.37,
            1.48,
            SizeClass.XXS,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("SCEPTILE"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            48.17,
            1.64,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("VENUSAUR"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            48.65,
            1.51,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("CAMERUPT"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            216.79,
            1.94,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("SLOWBRO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            42.96,
            1.23,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("MAWILE"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            15.04,
            0.66,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("AUDINO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            19.04,
            0.85,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("SHARPEDO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            103.72,
            1.76,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("ABSOL"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            53.63,
            1.33,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("HERACROSS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            68.49,
            1.64,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("HERACROSS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            78.89,
            1.83,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("AMPHAROS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            62.69,
            1.35,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("GALLADE"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            63.47,
            1.89,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("LATIOS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            53.79,
            2.03,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("LATIOS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            77.63,
            2.27,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("GARCHOMP"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            123.46,
            2.07,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("GARCHOMP"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            87.26,
            1.9,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("SALAMENCE"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            112.23,
            1.71,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("FALINKS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            45.28,
            2.62,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("PINSIR"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            71.89,
            1.68,
            SizeClass.M,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("ABOMASNOW"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            22.54,
            1.09,
            SizeClass.XXS,
        )
    )  # 19.45, 1.09
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("LATIAS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            12.13,
            0.7,
            SizeClass.XXS,
        )
    )  # 10.0, 0.
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("LATIOS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            14.28,
            0.99,
            SizeClass.XXS,
        )
    )  # 12.68, 0.99
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("STEELIX"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            164.34,
            6.63,
            SizeClass.XS,
        )
    )  # 251.17, 6.63
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("BEEDRILL"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            13.3,
            0.68,
            SizeClass.XS,
        )
    )  # 9.26, 0.68
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("SWAMPERT"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            49.27,
            0.98,
            SizeClass.XS,
        )
    )  # 41.51, 0.98
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("FALINKS"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            87.72,
            4.57,
            SizeClass.XXL,
        )
    )  # 750.63, 4.57
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("VENUSAUR"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            181.58,
            3.35,
            SizeClass.XXL,
        )
    )  # 267.94, 3.68
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("PIDGEOT"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            71.34,
            2.04,
            SizeClass.XL,
        )
    )  # 63.99, 2.51
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("ALAKAZAM"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA,
            83.69,
            2.5,
            SizeClass.XXL,
        )
    )  # 63.12, 1.84
    # https://www.threads.com/@cody_02_27/post/DZXottzk1yo
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("MEWTWO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_X,
            191.56,
            3.14,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("MEWTWO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_Y,
            191.56,
            3.14,
            SizeClass.XXL,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("KYOGRE"),
            HoloTempEvoId.TEMP_EVOLUTION_PRIMAL,
            143.15,
            3.44,
            SizeClass.M,
        )
    )  # 430.0, 3.44
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("MEWTWO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_X,
            30.19,
            0.99,
            SizeClass.XXS,
        )
    )
    print_size(
        evolution_size_range(
            PokeSpecies.resolve("MEWTWO"),
            HoloTempEvoId.TEMP_EVOLUTION_MEGA_Y,
            30.19,
            0.99,
            SizeClass.XXS,
        )
    )
