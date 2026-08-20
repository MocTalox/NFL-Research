from __future__ import annotations

from dataclasses import dataclass

from nfl.io import Message
from nfl.proto import HoloCardType, HoloLocationCard


@dataclass(frozen=True)
class LocationCardSettings:
    location_card: HoloLocationCard
    image_url: str
    card_type: HoloCardType | None
    vfx_address: str | None

    @classmethod
    def from_message(cls, msg: Message) -> LocationCardSettings:
        return cls(
            location_card=msg.get_enum("locationCard", HoloLocationCard),
            image_url=msg.get_string("imageUrl"),
            card_type=msg.get_enum_or_none("cardType", HoloCardType),
            vfx_address=msg.get_string_or_none("vfxAddress"),
        )
