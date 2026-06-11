from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class BattleSettings:
    retarget_seconds: float
    enemy_attack_interval: float
    round_duration_seconds: int
    bonus_time_per_ally_seconds: int
    maximum_attackers_per_battle: int
    same_type_attack_bonus_multiplier: float
    maximum_energy: int
    energy_delta_per_health_lost: float
    dodge_duration_ms: int
    swap_duration_ms: int
    dodge_damage_reduction_percent: float
    shadow_pokemon_attack_bonus_multiplier: float
    shadow_pokemon_defense_bonus_multiplier: float
    purified_pokemon_attack_multiplier_vs_shadow: float
    boss_energy_regeneration_per_health_lost: float

    @classmethod
    def from_message(cls, msg: Message) -> BattleSettings:
        return cls(
            retarget_seconds=msg.get_float("retargetSeconds"),
            enemy_attack_interval=msg.get_float("enemyAttackInterval"),
            round_duration_seconds=msg.get_int("roundDurationSeconds"),
            bonus_time_per_ally_seconds=msg.get_int("bonusTimePerAllySeconds"),
            maximum_attackers_per_battle=msg.get_int("maximumAttackersPerBattle"),
            same_type_attack_bonus_multiplier=msg.get_float("sameTypeAttackBonusMultiplier"),
            maximum_energy=msg.get_int("maximumEnergy"),
            energy_delta_per_health_lost=msg.get_float("energyDeltaPerHealthLost"),
            dodge_duration_ms=msg.get_int("dodgeDurationMs"),
            swap_duration_ms=msg.get_int("swapDurationMs"),
            dodge_damage_reduction_percent=msg.get_float("dodgeDamageReductionPercent"),
            shadow_pokemon_attack_bonus_multiplier=msg.get_float("shadowPokemonAttackBonusMultiplier"),
            shadow_pokemon_defense_bonus_multiplier=msg.get_float("shadowPokemonDefenseBonusMultiplier"),
            purified_pokemon_attack_multiplier_vs_shadow=msg.get_float("purifiedPokemonAttackMultiplierVsShadow"),
            boss_energy_regeneration_per_health_lost=msg.get_float("bossEnergyRegenerationPerHealthLost"),
        )
