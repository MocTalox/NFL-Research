from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class CombatSettings:
    round_duration_seconds: int
    turn_duration_seconds: float
    same_type_attack_bonus_multiplier: float
    fast_attack_bonus_multiplier: float
    charge_attack_bonus_multiplier: float
    defense_bonus_multiplier: float
    max_energy: int
    defender_minigame_multiplier: float
    quick_swap_cooldown_duration_seconds: int
    charge_score_base: float
    charge_score_nice: float
    charge_score_great: float
    charge_score_excellent: float
    shadow_pokemon_attack_bonus_multiplier: float
    shadow_pokemon_defense_bonus_multiplier: float
    purified_pokemon_attack_multiplier_vs_shadow: float

    @classmethod
    def from_message(cls, msg: Message) -> CombatSettings:
        return cls(
            round_duration_seconds=msg.get_int("roundDurationSeconds"),
            turn_duration_seconds=msg.get_float("turnDurationSeconds"),
            same_type_attack_bonus_multiplier=msg.get_float("sameTypeAttackBonusMultiplier"),
            fast_attack_bonus_multiplier=msg.get_float("fastAttackBonusMultiplier"),
            charge_attack_bonus_multiplier=msg.get_float("chargeAttackBonusMultiplier"),
            defense_bonus_multiplier=msg.get_float("defenseBonusMultiplier"),
            max_energy=msg.get_int("maxEnergy"),
            defender_minigame_multiplier=msg.get_float("defenderMinigameMultiplier"),
            quick_swap_cooldown_duration_seconds=msg.get_int("quickSwapCooldownDurationSeconds"),
            charge_score_base=msg.get_float("chargeScoreBase"),
            charge_score_nice=msg.get_float("chargeScoreNice"),
            charge_score_great=msg.get_float("chargeScoreGreat"),
            charge_score_excellent=msg.get_float("chargeScoreExcellent"),
            shadow_pokemon_attack_bonus_multiplier=msg.get_float("shadowPokemonAttackBonusMultiplier"),
            shadow_pokemon_defense_bonus_multiplier=msg.get_float("shadowPokemonDefenseBonusMultiplier"),
            purified_pokemon_attack_multiplier_vs_shadow=msg.get_float("purifiedPokemonAttackMultiplierVsShadow"),
        )
