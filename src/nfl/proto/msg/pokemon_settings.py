from __future__ import annotations
from dataclasses import dataclass
from nfl.proto.holoholo import HoloPokemonType, HoloPokemonClass, HoloTempEvoId, HoloPokemonId, HoloPokemonFamilyId, HoloPokemonForm, HoloPokemonMove
from nfl.proto.message import Message


@dataclass(frozen=True)
class PokemonSettings:
    pokemon_id: HoloPokemonId
    type: HoloPokemonType
    type_2: HoloPokemonType
    stats: Stats
    quick_moves: tuple[HoloPokemonMove, ...]
    cinematic_moves: tuple[HoloPokemonMove, ...]
    pokedex_height_m: float
    pokedex_weight_kg: float
    height_std_dev: float
    weight_std_dev: float
    family_id: HoloPokemonFamilyId
    evolution_branch: tuple[EvolutionBranch, ...]
    shadow: Shadow | None
    form: HoloPokemonForm
    elite_cinematic_move: tuple[HoloPokemonMove, ...]
    temp_evo_overrides: tuple[TempEvoOverrides, ...]
    elite_quick_move: tuple[HoloPokemonMove, ...]
    pokemon_class: HoloPokemonClass
    non_tm_cinematic_moves: tuple[HoloPokemonMove, ...]
    legacy_quick_moves: tuple[HoloPokemonMove, ...]
    legacy_cinematic_moves: tuple[HoloPokemonMove, ...]

    @classmethod
    def from_message(cls, msg: Message) -> PokemonSettings:
        return cls(
            pokemon_id=msg.get_enum("pokemonId", HoloPokemonId),
            type=msg.get_enum("type", HoloPokemonType),
            type_2=msg.get_enum_or_none("type2", HoloPokemonType),
            stats=msg.get_object("stats", Stats.from_message),
            quick_moves=msg.get_enum_list("quickMoves", HoloPokemonMove),
            cinematic_moves=msg.get_enum_list("cinematicMoves", HoloPokemonMove),
            pokedex_height_m=msg.get_float("pokedexHeightM"),
            pokedex_weight_kg=msg.get_float("pokedexWeightKg"),
            height_std_dev=msg.get_float("heightStdDev"),
            weight_std_dev=msg.get_float("weightStdDev"),
            family_id=msg.get_enum("familyId", HoloPokemonFamilyId),
            evolution_branch=msg.get_object_list("evolutionBranch", EvolutionBranch.from_message, "evolution"),
            shadow=msg.get_object_or_none("shadow", Shadow.from_message),
            form=msg.get_enum_or_none("form", HoloPokemonForm),
            elite_cinematic_move=msg.get_enum_list("eliteCinematicMove", HoloPokemonMove),
            temp_evo_overrides=msg.get_object_list("temp_evo_overrides", TempEvoOverrides.from_message, "tempEvoId"),
            elite_quick_move=msg.get_enum_list("eliteQuickMove", HoloPokemonMove),
            pokemon_class=msg.get_enum_or_none("pokemonClass", HoloPokemonClass),
            non_tm_cinematic_moves=msg.get_enum_list("nonTmCinematicMoves", HoloPokemonMove),
            legacy_quick_moves=msg.get_enum_list("legacyQuickMoves", HoloPokemonMove),
            legacy_cinematic_moves=msg.get_enum_list("legacyCinematicMoves", HoloPokemonMove),
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
    evolution: HoloPokemonId
    form: HoloPokemonForm

    @classmethod
    def from_message(cls, msg: Message) -> EvolutionBranch:
        return cls(
            evolution=msg.get_enum("evolution", HoloPokemonId),
            form=msg.get_enum_or_none("form", HoloPokemonForm),
        )

@dataclass(frozen=True)
class Shadow:
    purification_stardust_needed: int
    purification_candy_needed: int
    purified_charge_move: HoloPokemonMove
    shadow_charge_move: HoloPokemonMove

    @classmethod
    def from_message(cls, msg: Message) -> Shadow:
        return cls(
            purification_stardust_needed=msg.get_int("purificationStardustNeeded"),
            purification_candy_needed=msg.get_int("purificationCandyNeeded"),
            purified_charge_move=msg.get_enum("purifiedChargeMove", HoloPokemonMove),
            shadow_charge_move=msg.get_enum("shadowChargeMove", HoloPokemonMove),
        )

@dataclass(frozen=True)
class TempEvoOverrides:
    temp_evo_id: HoloTempEvoId
    stats: Stats
    average_height_m: float
    average_weight_kg: float
    type_override_1: HoloPokemonType
    type_override_2: HoloPokemonType

    @classmethod
    def from_message(cls, msg: Message) -> TempEvoOverrides:
        return cls(
            temp_evo_id=msg.get_enum("tempEvoId", HoloTempEvoId),
            stats=msg.get_object("stats", Stats.from_message),
            average_height_m=msg.get_float("averageHeightM"),
            average_weight_kg=msg.get_float("averageWeightKg"),
            type_override_1=msg.get_enum("typeOverride1", HoloPokemonType),
            type_override_2=msg.get_enum_or_none("typeOverride2", HoloPokemonType),
        )
