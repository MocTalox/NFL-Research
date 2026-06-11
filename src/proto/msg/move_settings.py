from __future__ import annotations
from dataclasses import dataclass
from proto.message import Message


@dataclass(frozen=True)
class MoveSettings:
    movement_id: str
    pokemon_type: str
    power: float
    duration_ms: int
    energy_delta: int

    @classmethod
    def from_message(cls, msg: Message) -> MoveSettings:
        return cls(
            movement_id=msg.get_string("movementId"),
            pokemon_type=msg.get_string("pokemonType"),
            power=msg.get_float_or_zero("power"),
            duration_ms=msg.get_int_or_zero("durationMs"),
            energy_delta=msg.get_int_or_zero("energyDelta"),
        )
