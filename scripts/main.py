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


def tgr_service_all():
    from nfl.models import TgrMovesetData
    from nfl.proto import HoloPokemonType
    from nfl.service import tgr_best_attackers

    for typing in HoloPokemonType:
        if typing is HoloPokemonType.UNDEFINED:
            continue
        rank: CsvList[TgrMovesetData] = CsvList()
        rank.add_colum("Pokemon", lambda r: str(r.moveset.pokemon))
        rank.add_colum("Fast Move", lambda r: str(r.moveset.quick))
        rank.add_colum("Dmg per Turn", lambda r: r.damage_per_turn)
        rank.add_colum("Survival", lambda r: r.total_bulk)

        for pokemon in tgr_best_attackers(enemy_type=typing):
            rank.add_row(pokemon)

        save_csv(rank, f"_ranking_{typing}")


def tgr_service_all_for():
    from nfl.models import TgrMovesetData
    from nfl.proto import HoloPokemonType
    from nfl.service import tgr_best_attackers

    for typing in HoloPokemonType:
        if typing is HoloPokemonType.UNDEFINED:
            continue
        rank: CsvList[TgrMovesetData] = CsvList()
        rank.add_colum("Pokemon", lambda r: str(r.moveset.pokemon))
        rank.add_colum("Fast Move", lambda r: str(r.moveset.quick))
        rank.add_colum("Dmg per Turn", lambda r: r.damage_per_turn)
        rank.add_colum("Survival", lambda r: r.total_bulk)

        for pokemon in tgr_best_attackers(pokemon_type=typing):
            rank.add_row(pokemon)

        save_csv(rank, f"_ranking_{typing}")


def tgr_service_single():
    from nfl.data import PokeSpecies
    from nfl.models import TgrMovesetData
    from nfl.service import tgr_best_pokemon_moveset

    rank: CsvList[TgrMovesetData] = CsvList()
    rank.add_colum("Pokemon", lambda r: str(r.moveset.pokemon))
    rank.add_colum("Fast Move", lambda r: str(r.moveset.quick))
    rank.add_colum("Charge Move", lambda r: str(r.moveset.charge))
    rank.add_colum("Dmg per Turn", lambda r: r.damage_per_turn)
    rank.add_colum("Charge Dmg", lambda r: r.charge_damage)
    rank.add_colum("Charge Inxed", lambda r: r.charge_index)
    rank.add_colum("Charge Rate", lambda r: r.charge_rate)
    rank.add_colum("Survival", lambda r: r.total_bulk)

    for pokemon in tgr_best_pokemon_moveset(
        PokeSpecies.resolve("Metagross", alignment="Shadow")
    ):
        rank.add_row(pokemon)

    save_csv(rank, "_ranking")


def debug_tgr_service():
    from nfl.service.tgr_service import get_all_pokemon

    save_text("\n".join(str(p) for p in get_all_pokemon()), "_tgr_species.txt")


def debug_ext_service():
    from nfl.service.extended_service import get_all_pokemon

    save_text("\n".join(str(p) for p in get_all_pokemon()), "_ext_species.txt")


def debug_proto_file():
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


##### MAIN SCRIPT #####

if __name__ == "__main__":
    from time import perf_counter

    start = perf_counter()

    # Main code start
    tgr_service_all()
    # Main code end

    print(f"Execution time: {perf_counter() - start:.3f}s")
