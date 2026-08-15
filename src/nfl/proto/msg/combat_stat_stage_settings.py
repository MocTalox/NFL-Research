from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class CombatStatStageSettings:
    minimum_stat_stage: int
    maximum_stat_stage: int
    attack_buff_multiplier: tuple[float, ...]
    defense_buff_multiplier: tuple[float, ...]

    @classmethod
    def from_message(cls, msg: Message) -> CombatStatStageSettings:
        return cls(
            minimum_stat_stage=msg.get_int("minimumStatStage"),
            maximum_stat_stage=msg.get_int("maximumStatStage"),
            attack_buff_multiplier=msg.get_float_list("attackBuffMultiplier"),
            defense_buff_multiplier=msg.get_float_list("defenseBuffMultiplier"),
        )
