from dataclasses import dataclass
from itertools import product
from typing import Iterator, Protocol
import math

from core.gm_holoholo import HoloPokemonType, HoloPokemonMove, HoloTempEvoId
from proto.msg.combat_move import CombatMove
from proto.msg.pokemon_settings import PokemonSettings
from service.common.data import PVP_MOVES, POKEMON, get_temp_evo_pokemon_settings
from service.logic.damage_formula import get_stab, get_effect, get_shadow_attack_bonus
from utils.poke_data import PokeData, gen_pokemon_data
from utils.poke_species import PokeSpecies


@dataclass(frozen=True)
class _PokemonData(PokeSpecies):
    type_1: HoloPokemonType
    type_2: HoloPokemonType
    attack: int
    defense: int
    stamina: int
    quick_moves: list[HoloPokemonMove]
    charged_moves: list[HoloPokemonMove]

    def is_the_same(self, other: PokeSpecies) -> bool:
        if not isinstance(other, _PokemonData):
            return False
        if self is other:
            return True
        return (
            self.name == other.name
            and self.temp_evo == other.temp_evo
            and self.shadow == other.shadow
            and self.type_1 == other.type_1
            and self.type_2 == other.type_2
            and self.attack == other.attack
            and self.defense == other.defense
            and self.stamina == other.stamina
            and self.quick_moves == other.quick_moves
            and self.charged_moves == other.charged_moves
        )

@dataclass(frozen=True)
class _EnemyData:
    type_1: HoloPokemonType
    type_2: HoloPokemonType
    defense: int
    shadow: bool

@dataclass(frozen=True)
class _PokemonMoveSet:
    pokemon: _PokemonData
    quick: CombatMove
    charged: CombatMove

@dataclass(frozen=True)
class MoveSetRanking:
    pokemon: _PokemonMoveSet #TODO visibility or structure fix
    damage_per_turn: float
    charged_damage: float
    charged_index: float
    charged_rate: float
    total_bulk: float

class _StatCalculator(Protocol):

    def __call__(
        self,
        quick: CombatMove,
        charged: CombatMove,
        quick_multiplier: float,
        charged_multiplier: float
    ) -> float:
        ...


def _to_pokemon_data(
    pokemon_settings: PokemonSettings,
    temp_evo_id: HoloTempEvoId = HoloTempEvoId(0),
    shadow: bool = False
):

    if temp_evo_id:
        pokemon_settings = get_temp_evo_pokemon_settings(pokemon_settings, temp_evo_id)

    quick_moves = [
        *pokemon_settings.quick_moves,
        *pokemon_settings.elite_quick_move,
    ]
    charged_moves = [
        *pokemon_settings.cinematic_moves,
        *pokemon_settings.elite_cinematic_move,
        *pokemon_settings.non_tm_cinematic_moves,
    ]

    if pokemon_settings.shadow is not None:
        if shadow:
            charged_moves.append(pokemon_settings.shadow.shadow_charge_move)
        else:
            charged_moves.append(pokemon_settings.shadow.purified_charge_move)

    return _PokemonData(
        name=pokemon_settings.pokemon_id,
        form=pokemon_settings.form,
        temp_evo=temp_evo_id,
        shadow=shadow,
        type_1=pokemon_settings.type,
        type_2=pokemon_settings.type_2,
        attack=pokemon_settings.stats.base_attack,
        defense=pokemon_settings.stats.base_defense,
        stamina=pokemon_settings.stats.base_stamina,
        quick_moves=quick_moves,
        charged_moves=charged_moves,
    )

def _unfold_settings(pokemon_settings: PokemonSettings):

    res: list[_PokemonData] = []

    res.append(_to_pokemon_data(pokemon_settings))

    if pokemon_settings.shadow:
        res.append(_to_pokemon_data(pokemon_settings, shadow=True))
    for temp_evo in pokemon_settings.temp_evo_overrides:
        res.append(_to_pokemon_data(pokemon_settings, temp_evo_id=temp_evo.temp_evo_id))

    return res

_POKEMON_DATA: PokeData[_PokemonData] = gen_pokemon_data(POKEMON, _unfold_settings)

def get_all_pokemon() -> list[PokeSpecies]:
    return sorted(_POKEMON_DATA.get_all_species())


# =========================
# DATA GENERATION
# =========================

def _gen_pokemon_instances(poke: _PokemonData, include_charged: bool = False) -> Iterator[_PokemonMoveSet]:
    poke_charged_moves = poke.charged_moves if include_charged else poke.charged_moves[:1]

    for quick, charged in product(poke.quick_moves, poke_charged_moves):
        yield _PokemonMoveSet(poke, PVP_MOVES[quick], PVP_MOVES[charged])

# =========================
# RANKING
# =========================

def tgr_best_pokemon_moveset(poke_species: PokeSpecies) -> list[MoveSetRanking]:

    pokemon = _POKEMON_DATA.get(poke_species)
    if not pokemon:
        raise ValueError()

    defender = _EnemyData(HoloPokemonType(0), HoloPokemonType(0), 150, True)

    rankings = [
        _create_ranking(p, defender)
        for p in _gen_pokemon_instances(pokemon, True)
    ]

    return sorted(
        rankings,
        key=lambda r: (r.damage_per_turn, r.charged_index),
        reverse=True
    )

def tgr_best_attackers_for_type(type: HoloPokemonType, limit: int) -> list[MoveSetRanking]:

    defender = _EnemyData(HoloPokemonType(0), HoloPokemonType(0), 150, True)
    return _best_attackers(defender, type, limit)

def tgr_best_attackers_against_type(type: HoloPokemonType, limit: int) -> list[MoveSetRanking]:

    defender = _EnemyData(type, HoloPokemonType(0), 150, True)
    return _best_attackers(defender, None, limit)

def _best_attackers(
    defender: _EnemyData,
    type: HoloPokemonType | None,
    limit: int
) -> list[MoveSetRanking]:

    rankings: list[MoveSetRanking] = []

    for poke in _POKEMON_DATA.get_all_pokes():

        candidates = (p for p in _gen_pokemon_instances(poke) if not type or p.quick.type == type)
        best = max(candidates, key=lambda p: _tgr_calc_damage_per_turn(p, defender), default=None)

        if best is not None:
            rankings.append(_create_ranking(best, defender))

    return sorted(rankings, key=lambda r: r.damage_per_turn, reverse=True)[:limit]

def _create_ranking(poke: _PokemonMoveSet, defender: _EnemyData) -> MoveSetRanking:

    return MoveSetRanking(
        pokemon=poke,
        damage_per_turn=_tgr_calc_damage_per_turn(poke, defender),
        charged_damage=_tgr_calc_charged_damage(poke, defender),
        charged_index=_tgr_calc_charged_index(poke, defender),
        charged_rate=_tgr_calc_charged_rate(poke, defender),
        total_bulk=_tgr_calc_total_bulk(poke, defender),
    )

# =========================
# CALCULATIONS
# =========================

def _tgr_calc_damage_per_turn(attacker: _PokemonMoveSet, defender: _EnemyData) -> float:
    return _calculate_stat(attacker, defender, _calc_damage_per_turn)

def _tgr_calc_charged_damage(attacker: _PokemonMoveSet, defender: _EnemyData) -> float:
    return _calculate_stat(attacker, defender, _calc_charged_damage)

def _tgr_calc_charged_index(attacker: _PokemonMoveSet, defender: _EnemyData) -> float:
    return _calculate_stat(attacker, defender, _calc_charged_index)

def _tgr_calc_charged_rate(attacker: _PokemonMoveSet, defender: _EnemyData) -> float:
    return _calculate_stat(attacker, defender, _calc_charged_rate)

def _tgr_calc_total_bulk(attacker: _PokemonMoveSet, defender: _EnemyData) -> float:
    #TODO As for now works as defender has just type_1
    # Consider adding a "move_type" to _EnemyData maybe
    stab = get_stab(defender.type_1, defender.type_1, defender.type_2)
    effect = get_effect(defender.type_1, attacker.pokemon.type_1, attacker.pokemon.type_2)
    shadow = get_shadow_attack_bonus(defender.shadow, attacker.pokemon.shadow)
    mults = stab * effect * shadow
    return (attacker.pokemon.defense + 15) * (attacker.pokemon.stamina + 15) / mults

# =========================
# CORE MATH
# =========================

def _calc_damage_per_turn(
    quick: CombatMove,
    charged: CombatMove,
    quick_multiplier: float,
    charged_multiplier: float
) -> float:

    return quick.power * quick_multiplier / (quick.duration_turns + 1)

def _calc_charged_damage(
    quick: CombatMove,
    charged: CombatMove,
    quick_multiplier: float,
    charged_multiplier: float
) -> float:

    return charged.power * charged_multiplier

def _calc_charged_index(
    quick: CombatMove,
    charged: CombatMove,
    quick_multiplier: float,
    charged_multiplier: float
) -> float:

    damage_per_turn = _calc_damage_per_turn(
        quick,
        charged,
        quick_multiplier,
        charged_multiplier
    )

    charged_damage = _calc_charged_damage(
        quick,
        charged,
        quick_multiplier,
        charged_multiplier
    )

    if damage_per_turn == 0:
        return math.inf
    return charged_damage / (20 * damage_per_turn)

def _calc_charged_rate(
    quick: CombatMove,
    charged: CombatMove,
    quick_multiplier: float,
    charged_multiplier: float
) -> float:

    if quick.energy_delta == 0:
        return math.inf
    return -1 * (quick.duration_turns + 1) * charged.energy_delta / quick.energy_delta

def _calculate_stat(
    attacker: _PokemonMoveSet,
    defender: _EnemyData,
    calculator: _StatCalculator
) -> float:

    base_multiplier = (
        get_shadow_attack_bonus(attacker.pokemon.shadow, defender.shadow)
        * (attacker.pokemon.attack + 15)
        / (defender.defense + 15)
    )

    quick_multiplier = base_multiplier * _move_params(
        attacker.quick,
        attacker.pokemon,
        defender
    )

    charged_multiplier = base_multiplier * _move_params(
        attacker.charged,
        attacker.pokemon,
        defender
    )

    return calculator(
        attacker.quick,
        attacker.charged,
        quick_multiplier,
        charged_multiplier
    )

def _move_params(
    move: CombatMove,
    attacker: _PokemonData,
    defender: _EnemyData
) -> float:

    return (
        get_stab(move.type, attacker.type_1, attacker.type_2)
        * get_effect(move.type, defender.type_1, defender.type_2)
    )
