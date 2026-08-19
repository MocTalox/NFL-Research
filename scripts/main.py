from typing import TypeVar

from nfl.utils import CsvList

T = TypeVar("T")

##### Utilities #####


def save_text(text: str, file_name: str) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(text)


def save_csv(csv_list: CsvList[T], file_name: str) -> None:
    save_text(str(csv_list), f"{file_name}.csv")


##### Callers #####


def proto():
    from scripts.proto_summary import GMProto

    for proto in [
        "temporaryEvolutionSettings",
    ]:
        print(f'Proto "{proto}"')
        print(GMProto.extract_proto(proto))


def breakpoints():
    import breakpoints

    res = "\n".join([";".join([str(y) for y in x]) for x in breakpoints.run()])
    save_text(res, "_out.txt")


def sizes_check():
    import sizes_check

    sizes_check.run()


def evo_sizes():
    import evo_sizes

    evo_sizes.run()


def showcases():
    import showcases

    showcases.run()


def negative_megas():
    import negative_megas

    negative_megas.run()


def tgr_service_all():
    from nfl.proto import HoloPokemonType
    from nfl.service.tgr_service import MoveSetRanking, tgr_best_attackers_against_type

    for typing in HoloPokemonType:
        rank: CsvList[MoveSetRanking] = CsvList()
        rank.add_colum("Pokemon", lambda r: str(r.pokemon.pokemon))
        rank.add_colum("Fast Move", lambda r: str(r.pokemon.quick.unique_id))
        rank.add_colum("Dmg per Turn", lambda r: r.damage_per_turn)
        rank.add_colum("Survival", lambda r: r.total_bulk)

        for pokemon in tgr_best_attackers_against_type(typing, 50):
            rank.add_row(pokemon)

        save_csv(rank, f"_ranking_{typing}")


def tgr_service_all_for():
    from nfl.proto import HoloPokemonType
    from nfl.service.tgr_service import MoveSetRanking, tgr_best_attackers_for_type

    for typing in HoloPokemonType:
        rank: CsvList[MoveSetRanking] = CsvList()
        rank.add_colum("Pokemon", lambda r: str(r.pokemon.pokemon))
        rank.add_colum("Fast Move", lambda r: str(r.pokemon.quick.unique_id))
        rank.add_colum("Dmg per Turn", lambda r: r.damage_per_turn)
        rank.add_colum("Survival", lambda r: r.total_bulk)

        for pokemon in tgr_best_attackers_for_type(typing, 50):
            rank.add_row(pokemon)

        save_csv(rank, f"_ranking_{typing}")


def tgr_service_single():
    from nfl.data import PokeSpecies
    from nfl.service.tgr_service import (
        MoveSetRanking,
        tgr_best_pokemon_moveset,
    )

    rank: CsvList[MoveSetRanking] = CsvList()
    rank.add_colum("Pokemon", lambda r: str(r.pokemon.pokemon))
    rank.add_colum("Fast Move", lambda r: str(r.pokemon.quick.unique_id))
    rank.add_colum("Charged Move", lambda r: str(r.pokemon.charged.unique_id))
    rank.add_colum("Dmg per Turn", lambda r: r.damage_per_turn)
    rank.add_colum("Charged Dmg", lambda r: r.charged_damage)
    rank.add_colum("Charged Inxed", lambda r: r.charged_index)
    rank.add_colum("Charged Rate", lambda r: r.charged_rate)
    rank.add_colum("Survival", lambda r: r.total_bulk)

    for pokemon in tgr_best_pokemon_moveset(
        PokeSpecies.resolve("Metagross", shadow=True)
    ):
        rank.add_row(pokemon)

    save_csv(rank, "_ranking")


def debug_tgr_service():
    from nfl.service.tgr_service import get_all_pokemon

    save_text("\n".join(str(p) for p in get_all_pokemon()), "_tgr_species.txt")


def debug_ext_service():
    from nfl.service.extended_service import get_all_pokemon

    save_text("\n".join(str(p) for p in get_all_pokemon()), "_ext_species.txt")


def main():
    from nfl import data
    from nfl.calcs import SizedPokemon, evolution_size
    from nfl.data import PokeSpecies, SizeClass
    from nfl.utils import f32

    ps = data.get_pokemon_settings(PokeSpecies.resolve("Shroodle"))
    pes = data.get_pokemon_extended_settings(PokeSpecies.resolve("Shroodle"))
    assert ps and pes
    res = evolution_size(
        SizedPokemon.build(
            pokemon=PokeSpecies.resolve("CORPHISH"),
            weight_kg=24.26,
            height_m=0.89,
            size_class=SizeClass.XL,
        ),
        PokeSpecies.resolve("CRAWDAUNT"),
    )
    print(res)
    return
    from nfl.cals import ShowcasePokemon, contest_score

    from nfl import data
    from nfl.data import PokeSpecies, SizeClass
    from nfl.utils import f32

    ps = data.get_pokemon_settings(PokeSpecies.resolve("Shroodle"))
    pes = data.get_pokemon_extended_settings(PokeSpecies.resolve("Shroodle"))
    assert ps and pes
    res = contest_score(
        ShowcasePokemon(
            ps,
            pes.size_settings,
            individual_values=13 + 13 + 13,
            weight_kg=f32(1.165),
            height_m=f32(0.3),
            size_class=SizeClass.XXL,
        )
    )
    print(res)
    return
    from nfl import data

    print(list(data.FORM_POKEMON.items())[:50])
    return
    from nfl.io._proto_parser import Data, read_proto_file

    names: set[str] = set()
    vartypes: set[tuple[str, bool]] = set()

    def check_names(data: Data, current: list[str]):
        for d in data.childs:
            next = current + [d.name]
            for i in range(len(next)):
                names.add(".".join(next[i : len(next)]))
            check_names(d, next)

    def check_types(data: Data, current: str):
        vals: set[int] = set()
        for v in data.values:
            if v.value in vals:
                print(f'[ERROR] Dupe value "{v.value}" in {current}')
            vals.add(v.value)
        for f in data.fields:
            if f.value in vals:
                print(f'[ERROR] Dupe value "{f.value}" in {current}')
            vals.add(f.value)
            if f.var_type not in names:
                vartypes.add((f.var_type, f.repeated))
        for d in data.childs:
            check_types(d, f"{current}{d.name}.")

    check_names(read_proto_file(), [])
    check_types(read_proto_file(), "")
    print(len(names))
    for vartype, rep in vartypes:
        print(f"repeated {vartype}" if rep else vartype)
    return
    from nfl.proto import TEMPORARY_EVOLUTION_SETTINGS, HoloPokemonId

    for tes in TEMPORARY_EVOLUTION_SETTINGS:
        if tes.pokemon_id == HoloPokemonId.RAICHU:
            print(tes)
    return
    from nfl.proto import FORM_SETTINGS, POKEMON_SETTINGS, HoloPokemonId, game_master

    """
    for template in game_master()["friendshipMilestoneSettings"].values():
        print(f"template {template}")
    for template in game_master()["nonCombatMoveSettings"].values():
        print(f"template {template}")
    for template in game_master()["type_effective"].values():
        print(f"template {template}")
    for template in game_master()["weather_affinities"].values():
        print(f"template {template}")
    """
    for template in game_master()["formSettings"].values():
        if (
            template.value.get_enum("pokemon", HoloPokemonId)
            == HoloPokemonId.GIMMIGHOUL
        ):
            print(f"template {template}")
    for template in game_master()["pokemonSettings"].values():
        if (
            template.value.get_enum("pokemonId", HoloPokemonId)
            == HoloPokemonId.BAXCALIBUR
        ):
            print(f"template {template}")
    for form in FORM_SETTINGS:
        if form.pokemon == HoloPokemonId.GIMMIGHOUL:
            print(form)
    for pokemon in POKEMON_SETTINGS:
        if pokemon.pokemon_id == HoloPokemonId.BAXCALIBUR:
            print(pokemon)
    return
    from nfl.cals import (
        BattlePokemon,
        BattleState,
        damage_formula_raw,
        get_cpm,
        get_rcpm,
        get_tgr_hp,
    )

    from nfl.data import PVP_MOVES, PokeSpecies, get_pokemon_settings
    from nfl.proto import (
        HoloCharacterCategory,
        HoloCombatType,
        HoloPokemonMove,
    )

    e = PokeSpecies.resolve("excadrill")
    v = PokeSpecies.resolve("voltorb")
    eps = get_pokemon_settings(e)
    vps = get_pokemon_settings(v)
    assert eps and vps

    vrcpm = get_rcpm(80)
    vp = BattlePokemon(vps, 15, 15, 15, vrcpm, True, False, HoloCharacterCategory.GRUNT)
    vhp = get_tgr_hp(vps, vrcpm, vp.tgr_member, 15)
    print(f"Voltorb HP: {vhp}")

    m = PVP_MOVES[HoloPokemonMove.MUD_SLAP_FAST]
    b = BattleState(HoloCombatType.VS_SEEKER)

    for lvl in range(80, 101):
        lvl = lvl / 2
        cpm = get_cpm(lvl)
        ep = BattlePokemon(eps, 15, 15, 15, cpm, True, False)
        dmg = damage_formula_raw(ep, vp, m.power, m.type, 0, False, b)
        print(f"Level: {lvl} -> Damage: {int(dmg) + 1} ({dmg})")


##### MAIN SCRIPT #####

if __name__ == "__main__":
    from time import perf_counter

    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.3f}s")
