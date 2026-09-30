from dataclasses import dataclass

from .general import PokemonStats


@dataclass(frozen=True)
class TgrBreakpointsDamageResult:
    stat: int
    damage: int


@dataclass(frozen=True)
class TgrBreakpointsDamageByLevel:
    level: float
    damage_by_stat: list[TgrBreakpointsDamageResult]


@dataclass(frozen=True)
class TgrBreakpointsResult:
    enemy_stats: PokemonStats
    damage_by_level: list[TgrBreakpointsDamageByLevel]
