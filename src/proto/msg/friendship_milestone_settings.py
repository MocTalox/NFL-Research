from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class FriendshipMilestoneSettings:
    min_points_to_reach: int
    attack_bonus_percentage: float
    relative_points_to_reach: int

    @classmethod
    def from_message(cls, msg: Message) -> FriendshipMilestoneSettings:
        return cls(
            min_points_to_reach=msg.get_int_or_zero("minPointsToReach"),
            attack_bonus_percentage=msg.get_float("attackBonusPercentage"),
            relative_points_to_reach=msg.get_int_or_zero("relativePointsToReach"),
        )
