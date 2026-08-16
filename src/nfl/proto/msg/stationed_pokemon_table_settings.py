from __future__ import annotations
from dataclasses import dataclass
from nfl.proto.message import Message


@dataclass(frozen=True)
class StationedPokemonTableSettings:
    tier_boosts: tuple[TierBoosts, ...]

    @classmethod
    def from_message(cls, msg: Message) -> StationedPokemonTableSettings:
        return cls(
            tier_boosts=msg.get_object_list("tierBoosts", TierBoosts.from_message),
        )

@dataclass(frozen=True)
class TierBoosts:
    num_stationed: int
    num_boost_icons: int
    hundredths_of_percent: int

    @classmethod
    def from_message(cls, msg: Message) -> TierBoosts:
        return cls(
            num_stationed=msg.get_int("numStationed"),
            num_boost_icons=msg.get_int("numBoostIcons"),
            hundredths_of_percent=msg.get_int("hundredths_of_percent"),
        )
