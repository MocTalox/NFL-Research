from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class CombatMove:
    unique_id: str
    type: str
    power: float
    energy_delta: int
    buffs: Buffs | None
    duration_turns: int

    @classmethod
    def from_message(cls, msg: Message) -> CombatMove:
        return cls(
            unique_id=msg.get_string("uniqueId"),
            type=msg.get_string("type"),
            power=msg.get_float_or_zero("power"),
            energy_delta=msg.get_int_or_zero("energyDelta"),
            buffs=msg.get_object_or_none("buffs", Buffs.from_message),
            duration_turns=msg.get_int_or_zero("durationTurns"),
        )

@dataclass(frozen=True)
class Buffs:
    buff_activation_chance: float
    attacker_attack_stat_stage_change: int
    attacker_defense_stat_stage_change: int
    target_attack_stat_stage_change: int
    target_defense_stat_stage_change: int

    @classmethod
    def from_message(cls, msg: Message) -> Buffs:
        return cls(
            buff_activation_chance=msg.get_float_or_zero("buffActivationChance"),
            attacker_attack_stat_stage_change=msg.get_int_or_zero("attackerAttackStatStageChange"),
            attacker_defense_stat_stage_change=msg.get_int_or_zero("attackerDefenseStatStageChange"),
            target_attack_stat_stage_change=msg.get_int_or_zero("targetAttackStatStageChange"),
            target_defense_stat_stage_change=msg.get_int_or_zero("targetDefenseStatStageChange"),
        )
