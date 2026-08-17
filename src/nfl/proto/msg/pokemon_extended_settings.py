from __future__ import annotations

from dataclasses import dataclass

from nfl.data import Message
from nfl.proto import HoloPokemonForm, HoloPokemonId, HoloTempEvoId


@dataclass(frozen=True)
class PokemonExtendedSettings:
    unique_id: HoloPokemonId
    size_settings: SizeSettings
    form: HoloPokemonForm
    temp_evo_overrides: tuple[TempEvoOverrides_PES, ...]

    @classmethod
    def from_message(cls, msg: Message) -> PokemonExtendedSettings:
        return cls(
            unique_id=msg.get_enum("uniqueId", HoloPokemonId),
            size_settings=msg.get_object("sizeSettings", SizeSettings.from_message),
            form=msg.get_enum_or_none("form", HoloPokemonForm),
            temp_evo_overrides=msg.get_object_list(
                "temp_evo_overrides", TempEvoOverrides_PES.from_message
            ),
        )


@dataclass(frozen=True)
class TempEvoOverrides_PES:
    temp_evo_id: HoloTempEvoId
    size_settings: SizeSettings

    @classmethod
    def from_message(cls, msg: Message) -> TempEvoOverrides_PES:
        return cls(
            temp_evo_id=msg.get_enum("tempEvoId", HoloTempEvoId),
            size_settings=msg.get_object("sizeSettings", SizeSettings.from_message),
        )


@dataclass(frozen=True)
class SizeSettings:
    xxs_lower_bound: float
    xs_lower_bound: float
    m_lower_bound: float
    m_upper_bound: float
    xl_upper_bound: float
    xxl_upper_bound: float

    @classmethod
    def from_message(cls, msg: Message) -> SizeSettings:
        return cls(
            xxs_lower_bound=msg.get_float("xxsLowerBound"),
            xs_lower_bound=msg.get_float("xsLowerBound"),
            m_lower_bound=msg.get_float("mLowerBound"),
            m_upper_bound=msg.get_float("mUpperBound"),
            xl_upper_bound=msg.get_float("xlUpperBound"),
            xxl_upper_bound=msg.get_float("xxlUpperBound"),
        )
