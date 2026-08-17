from __future__ import annotations

from dataclasses import dataclass

from nfl.proto import HoloFriendshipLevel, Message


@dataclass(frozen=True)
class FriendshipMilestoneSettings:
    min_points_to_reach: int
    attack_bonus_percentage: float
    relative_points_to_reach: int
    friendship_level: HoloFriendshipLevel

    @classmethod
    def from_message(cls, msg: Message) -> FriendshipMilestoneSettings:
        return cls(
            min_points_to_reach=msg.get_int_or_zero("minPointsToReach"),
            attack_bonus_percentage=msg.get_float("attackBonusPercentage"),
            relative_points_to_reach=msg.get_int_or_zero("relativePointsToReach"),
            friendship_level=msg.get_enum("friendship_level", HoloFriendshipLevel),
        )
