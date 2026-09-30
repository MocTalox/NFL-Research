from __future__ import annotations

from dataclasses import dataclass

from .size_class import SizeClass
from .size_data import SizeData


@dataclass(frozen=True)
class SizeDataRange:
    lower_wei_lower_hei: SizeData
    lower_wei_upper_hei: SizeData
    upper_wei_lower_hei: SizeData
    upper_wei_upper_hei: SizeData
    weight_range: tuple[float, float]
    height_range: tuple[float, float]
    size_class_range: tuple[SizeClass, SizeClass]

    @classmethod
    def build(
        cls,
        lower_wei_lower_hei: SizeData,
        lower_wei_upper_hei: SizeData,
        upper_wei_lower_hei: SizeData,
        upper_wei_upper_hei: SizeData,
    ) -> SizeDataRange:
        weight_min = min(
            lower_wei_lower_hei.weight_kg,
            lower_wei_upper_hei.weight_kg,
            upper_wei_lower_hei.weight_kg,
            upper_wei_upper_hei.weight_kg,
        )
        weight_max = max(
            lower_wei_lower_hei.weight_kg,
            lower_wei_upper_hei.weight_kg,
            upper_wei_lower_hei.weight_kg,
            upper_wei_upper_hei.weight_kg,
        )
        height_min = min(
            lower_wei_lower_hei.height_m,
            lower_wei_upper_hei.height_m,
            upper_wei_lower_hei.height_m,
            upper_wei_upper_hei.height_m,
        )
        height_max = max(
            lower_wei_lower_hei.height_m,
            lower_wei_upper_hei.height_m,
            upper_wei_lower_hei.height_m,
            upper_wei_upper_hei.height_m,
        )
        size_class_min = min(
            lower_wei_lower_hei.size_class,
            lower_wei_upper_hei.size_class,
            upper_wei_lower_hei.size_class,
            upper_wei_upper_hei.size_class,
        )
        size_class_max = max(
            lower_wei_lower_hei.size_class,
            lower_wei_upper_hei.size_class,
            upper_wei_lower_hei.size_class,
            upper_wei_upper_hei.size_class,
        )

        return cls(
            lower_wei_lower_hei,
            lower_wei_upper_hei,
            upper_wei_lower_hei,
            upper_wei_upper_hei,
            (weight_min, weight_max),
            (height_min, height_max),
            (size_class_min, size_class_max),
        )
