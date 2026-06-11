from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class PokemonSettings:
    pokemon_id: str
    type: str
    type_2: str | None
    stats: Stats
    quick_moves: tuple[str, ...]
    cinematic_moves: tuple[str, ...]
    pokedex_height_m: float
    pokedex_weight_kg: float
    height_std_dev: float
    weight_std_dev: float
    family_id: str
    evolution_branch: tuple[EvolutionBranch, ...]
    shadow: Shadow | None
    form: str | None
    elite_cinematic_move: tuple[str, ...]
    temp_evo_overrides: tuple[TempEvoOverrides, ...]
    elite_quick_move: tuple[str, ...]
    pokemon_class: str | None
    non_tm_cinematic_moves: tuple[str, ...]

    @classmethod
    def from_message(cls, msg: Message) -> PokemonSettings:
        return cls(
            pokemon_id=msg.get_string("pokemonId"),
            type=msg.get_string("type"),
            type_2=msg.get_string_or_none("type2"),
            stats=msg.get_object("stats", Stats.from_message),
            quick_moves=msg.get_string_list("quickMoves"),
            cinematic_moves=msg.get_string_list("cinematicMoves"),
            pokedex_height_m=msg.get_float("pokedexHeightM"),
            pokedex_weight_kg=msg.get_float("pokedexWeightKg"),
            height_std_dev=msg.get_float("heightStdDev"),
            weight_std_dev=msg.get_float("weightStdDev"),
            family_id=msg.get_string("familyId"),
            evolution_branch=msg.get_object_list("evolutionBranch", EvolutionBranch.from_message, "evolution"),
            shadow=msg.get_object_or_none("shadow", Shadow.from_message),
            form=msg.get_string_or_none("form"),
            elite_cinematic_move=msg.get_string_list("eliteCinematicMove"),
            temp_evo_overrides=msg.get_object_list("temp_evo_overrides", TempEvoOverrides.from_message, "tempEvoId"),
            elite_quick_move=msg.get_string_list("eliteQuickMove"),
            pokemon_class=msg.get_string_or_none("pokemonClass"),
            non_tm_cinematic_moves=msg.get_string_list("nonTmCinematicMoves"),
        )

@dataclass(frozen=True)
class Stats:
    base_stamina: int
    base_attack: int
    base_defense: int

    @classmethod
    def from_message(cls, msg: Message) -> Stats:
        return cls(
            base_stamina=msg.get_int_or_zero("baseStamina"),
            base_attack=msg.get_int_or_zero("baseAttack"),
            base_defense=msg.get_int_or_zero("baseDefense"),
        )

@dataclass(frozen=True)
class EvolutionBranch:
    evolution: str
    form: str | None

    @classmethod
    def from_message(cls, msg: Message) -> EvolutionBranch:
        return cls(
            evolution=msg.get_string("evolution"),
            form=msg.get_string_or_none("form"),
        )

@dataclass(frozen=True)
class Shadow:
    purification_stardust_needed: int
    purification_candy_needed: int
    purified_charge_move: str
    shadow_charge_move: str

    @classmethod
    def from_message(cls, msg: Message) -> Shadow:
        return cls(
            purification_stardust_needed=msg.get_int("purificationStardustNeeded"),
            purification_candy_needed=msg.get_int("purificationCandyNeeded"),
            purified_charge_move=msg.get_string("purifiedChargeMove"),
            shadow_charge_move=msg.get_string("shadowChargeMove"),
        )

@dataclass(frozen=True)
class TempEvoOverrides:
    temp_evo_id: str
    stats: Stats
    average_height_m: float
    average_weight_kg: float
    type_override_1: str
    type_override_2: str | None

    @classmethod
    def from_message(cls, msg: Message) -> TempEvoOverrides:
        return cls(
            temp_evo_id=msg.get_string("tempEvoId"),
            stats=msg.get_object("stats", Stats.from_message),
            average_height_m=msg.get_float("averageHeightM"),
            average_weight_kg=msg.get_float("averageWeightKg"),
            type_override_1=msg.get_string("typeOverride1"),
            type_override_2=msg.get_string_or_none("typeOverride2"),
        )
