from enum import Enum

from pydantic import BaseModel, Field


class MessengerOptions(str, Enum):
    WHATSAPP = "WhatsApp"
    FACEBOOK = "Facebook"
    EMAIL = "Email"
    INSTAGRAM = "Instagram"
    OTHER = "Other"

    @classmethod
    def _missing_(cls, value):
        # Allow case-insensitive matching
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"{value} is not a valid MessengerOptions")


class DetectionTuple(BaseModel):
    switch: bool
    messenger: MessengerOptions = Field(
        description="Correctly assign one of the messengers"
    )
