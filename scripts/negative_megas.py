# pyright: reportUnknownMemberType=false, reportArgumentType=false

import matplotlib.pyplot as plt
import numpy as np

from nfl.calcs import SizedPokemon, evolution_size
from nfl.data import (
    FORM_SETTINGS,
    PokeSpecies,
    SizeClass,
    get_pokemon_extended_settings,
    get_pokemon_settings,
)
from nfl.proto import HoloPokemonForm


def create_plot(
    title: str,
    points: list[tuple[float, float, int]],
    wei: float = 1.0,
    hei: float = 1.0,
):
    # Preprocess:
    # (x, y, n) -> (x/100, (x/100)**n + y/100)
    points_aux = [(x, x**n + y) for x, y, n in points]

    # Separate x and y values
    x_values = [p[0] * hei for p in points_aux]
    y_values = [p[1] * wei for p in points_aux]

    # Generate x values for the functions
    x_func = np.linspace(0.49, 1.5, 500)
    x_func_xxl = np.linspace(1.5, 2.0, 50)

    # Define the functions
    y_func1 = x_func**2 - 0.5
    y_func2 = x_func**2 - 0.25
    y_func3 = x_func**2
    y_func4 = x_func**2 + 0.25
    y_func5 = x_func**2 + 0.5

    y_func1_xxl = x_func_xxl - 0.5
    y_func2_xxl = x_func_xxl - 0.25
    y_func3_xxl = x_func_xxl
    y_func4_xxl = x_func_xxl + 0.25
    y_func5_xxl = x_func_xxl + 0.5

    # Renormalize the functions
    x_func = x_func * hei
    y_func1 = y_func1 * wei
    y_func2 = y_func2 * wei
    y_func3 = y_func3 * wei
    y_func4 = y_func4 * wei
    y_func5 = y_func5 * wei

    x_func_xxl = x_func_xxl * hei
    y_func1_xxl = y_func1_xxl * wei
    y_func2_xxl = y_func2_xxl * wei
    y_func3_xxl = y_func3_xxl * wei
    y_func4_xxl = y_func4_xxl * wei
    y_func5_xxl = y_func5_xxl * wei

    # Other functions
    xxs_x_func = [0.5 * hei] * 2
    mxs_x_func = [0.75 * hei] * 2
    mxl_x_func = [1.25 * hei] * 2
    xxl_x_func = [1.5 * hei] * 2

    xxs_y_func = [0.0, (0.5**2 + 0.5) * wei]
    mxs_y_func = [(0.75**2 - 0.5) * wei, (0.75**2 + 0.5) * wei]
    mxl_y_func = [(1.25**2 - 0.5) * wei, (1.25**2 + 0.5) * wei]
    xxl_y_func = [(1.5 - 0.5) * wei, (1.5**2 + 0.5) * wei]

    # Create the graph
    plt.figure(figsize=(8, 5))

    plt.scatter(x_values, y_values, color="red", marker=".", s=50)

    # Plot the functions
    plt.plot(x_func, y_func1, color="blue", linewidth=2, label="f(x) = x² - 0.5")
    plt.plot(
        x_func,
        y_func2,
        color="blue",
        linewidth=1,
        alpha=0.5,
        linestyle=":",
        label="f(x) = x² - 0.25",
    )
    plt.plot(
        x_func,
        y_func3,
        color="blue",
        linewidth=1,
        alpha=0.5,
        linestyle="--",
        label="f(x) = x²",
    )
    plt.plot(
        x_func,
        y_func4,
        color="blue",
        linewidth=1,
        alpha=0.5,
        linestyle=":",
        label="f(x) = x² + 0.25",
    )
    plt.plot(x_func, y_func5, color="blue", linewidth=2, label="f(x) = x² + 0.5")

    plt.plot(
        x_func_xxl, y_func1_xxl, color="blue", linewidth=2, label="f(x) = x² - 0.5"
    )
    plt.plot(
        x_func_xxl,
        y_func2_xxl,
        color="blue",
        linewidth=1,
        alpha=0.5,
        linestyle=":",
        label="f(x) = x² - 0.25",
    )
    plt.plot(
        x_func_xxl,
        y_func3_xxl,
        color="blue",
        linewidth=1,
        alpha=0.5,
        linestyle="--",
        label="f(x) = x²",
    )
    plt.plot(
        x_func_xxl,
        y_func4_xxl,
        color="blue",
        linewidth=1,
        alpha=0.5,
        linestyle=":",
        label="f(x) = x² + 0.25",
    )
    plt.plot(
        x_func_xxl, y_func5_xxl, color="blue", linewidth=2, label="f(x) = x² + 0.5"
    )

    plt.plot(
        xxs_x_func,
        xxs_y_func,
        color="green",
        linewidth=1,
        alpha=0.5,
        linestyle="--",
        label="x = 0.5",
    )
    plt.plot(
        mxs_x_func,
        mxs_y_func,
        color="green",
        linewidth=1,
        alpha=0.5,
        linestyle="--",
        label="x = 0.75",
    )
    plt.plot(
        mxl_x_func,
        mxl_y_func,
        color="green",
        linewidth=1,
        alpha=0.5,
        linestyle="--",
        label="x = 1.25",
    )
    plt.plot(
        xxl_x_func,
        xxl_y_func,
        color="green",
        linewidth=1,
        alpha=0.5,
        linestyle="--",
        label="x = 1.5",
    )

    # Axis limits
    plt.xlim(0.49 * hei, 2.0 * hei)
    plt.ylim(0.0, 2.75 * wei)

    # Labels and title
    plt.xlabel("Height")
    plt.ylabel("Weight")
    plt.title(title)

    # Grid
    plt.grid(True)

    # Save image
    filename = f"test/{title.lower()}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")

    # Show image
    plt.close()

    print(f"Graph saved as {filename}")


def run():
    for fs in FORM_SETTINGS:
        p = get_pokemon_settings(PokeSpecies(name=fs.pokemon))
        e = get_pokemon_extended_settings(PokeSpecies(name=fs.pokemon))
        if fs.pokemon.name == "BASCULEGION":
            continue
        assert p and e
        for teo in p.temp_evo_overrides:
            poke = PokeSpecies(
                name=fs.pokemon,
                form=HoloPokemonForm.FORM_UNSET,
                temp_evo=teo.temp_evo_id,
            )
            res: list[tuple[float, float, int]] = []
            for hvi in range(49, 201):
                hv = hvi / 100
                h = hv * p.pokedex_height_m
                if h > e.size_settings.xxl_upper_bound:
                    continue
                s = SizeClass.from_height(h, e.size_settings)
                n = 1 if s == SizeClass.XXL else 2
                for wvi in range(-50, 51):
                    wv = wvi / 100
                    w = (wv + hv**n) * p.pokedex_weight_kg
                    if w <= 0:
                        w = (hv**n) * p.pokedex_weight_kg
                    _ = evolution_size(
                        SizedPokemon(poke, p, e, w, h, s),
                        teo.temp_evo_id,
                    )
                    if False:  # TODO hardcore activation
                        res.append((hv, wv, n))
            if res:
                create_plot(poke, res, p.pokedex_weight_kg, p.pokedex_height_m)
