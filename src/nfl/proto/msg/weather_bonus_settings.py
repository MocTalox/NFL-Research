from __future__ import annotations

from dataclasses import dataclass

from nfl.data import Message


@dataclass(frozen=True)
class WeatherBonusSettings:
    attack_bonus_multiplier: float

    @classmethod
    def from_message(cls, msg: Message) -> WeatherBonusSettings:
        return cls(
            attack_bonus_multiplier=msg.get_float("attackBonusMultiplier"),
        )
