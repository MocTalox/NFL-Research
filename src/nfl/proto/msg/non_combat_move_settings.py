from __future__ import annotations

from dataclasses import dataclass

from nfl.io import Message
from nfl.proto import HoloCombatType, HoloPokemonMove


@dataclass(frozen=True)
class NonCombatMoveSettings:
    unique_id: HoloPokemonMove
    bonus_effect: BonusEffect

    @classmethod
    def from_message(cls, msg: Message) -> NonCombatMoveSettings:
        return cls(
            unique_id=msg.get_enum("uniqueId", HoloPokemonMove),
            bonus_effect=msg.get_object("bonusEffect", BonusEffect.from_message),
        )


@dataclass(frozen=True)
class BonusEffect:
    attack_defense_bonus: AttackDefenseBonus | None

    @classmethod
    def from_message(cls, msg: Message) -> BonusEffect:
        return cls(
            attack_defense_bonus=msg.get_object_or_none(
                "attackDefenseBonus", AttackDefenseBonus.from_message
            ),
        )


@dataclass(frozen=True)
class AttackDefenseBonus:
    attributes: tuple[Attributes, ...]

    @classmethod
    def from_message(cls, msg: Message) -> AttackDefenseBonus:
        return cls(
            attributes=msg.get_object_list("attributes", Attributes.from_message),
        )


@dataclass(frozen=True)
class Attributes:
    combat_types: tuple[HoloCombatType, ...]
    attack_multiplier: float
    defense_multiplier: float

    @classmethod
    def from_message(cls, msg: Message) -> Attributes:
        return cls(
            combat_types=msg.get_enum_list("combatTypes", HoloCombatType),
            attack_multiplier=msg.get_float_or_zero("attackMultiplier"),
            defense_multiplier=msg.get_float_or_zero("defenseMultiplier"),
        )
