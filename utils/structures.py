from enum import Enum


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