from typing import Any

from api import PokeInput, get_pokemon_names, get_pokemon_forms, get_move_names, get_enemy_names, calculate_damage

class ApiBridge:

    def get_pokemon_names(self):
        return get_pokemon_names()

    def get_pokemon_forms(self, pokemon: str | None = None):
        return get_pokemon_forms(pokemon)

    def get_move_names(self, pokemon: str, form: str):
        return get_move_names(PokeInput(name=pokemon, form=form))

    def get_enemy_names(self):
        return get_enemy_names()

    def calculate_damage(self, request: dict[str, Any]):

        pokemon = PokeInput(**request["pokemon"])
        enemy_pokemon = PokeInput(**request["enemy_pokemon"])

        return calculate_damage(
            pokemon=pokemon,
            move=request["move"],
            min_atk=request["min_atk"],
            max_atk=request["max_atk"],
            min_level=request["min_level"],
            max_level=request["max_level"],
            enemy=request["enemy"],
            enemy_pokemon=enemy_pokemon,
            trainer_level=request["trainer_level"],
        )
