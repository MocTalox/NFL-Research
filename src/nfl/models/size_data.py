from __future__ import annotations

from dataclasses import dataclass

from nfl.exceptions import ValidationError
from nfl.proto import SizeSettings
from nfl.utils import has_decimals

from .size_class import SizeClass


@dataclass(frozen=True)
class SizeData:
    weight_kg: float
    height_m: float
    size_class: SizeClass

    @classmethod
    def build(
        cls,
        size_settings: SizeSettings,
        weight_kg: float,
        height_m: float,
        size_class: SizeClass | None = None,
    ) -> SizeData:
        if weight_kg < 0 or height_m < 0:
            raise ValidationError(
                "INVALID_POKÉMON_DIMENSIONS",
                weight_kg=weight_kg,
                height_m=height_m,
            )

        if size_class is None:
            size_class = SizeClass.from_height(height_m, size_settings)
        else:
            SizeData._validate_size_class(size_settings, height_m, size_class)

        return cls(weight_kg, height_m, size_class)

    def change_size(
        self, size_settings: SizeSettings, d_weight: float, d_height: float
    ) -> SizeData:
        height_min, height_max = self.size_class.get_bounds(size_settings)

        weight = max(self.weight_kg + d_weight, 0)
        height = max(min(self.height_m + d_height, height_max), height_min)

        return SizeData(weight, height, self.size_class)

    @staticmethod
    def _validate_size_class(
        size_settings: SizeSettings, height_m: float, size_class: SizeClass
    ):
        candidates = (
            (height_m - 0.005, height_m + 0.005)
            if has_decimals(height_m, 2)
            else (height_m,)
        )
        if any(size_class.in_bounds(h, size_settings) for h in candidates):
            return
        lower, upper = size_class.get_bounds(size_settings)
        raise ValidationError(
            "SIZE_CLASS_MISMATCH",
            height_m=height_m,
            size_class=size_class,
            lower=lower,
            upper=upper,
        )
