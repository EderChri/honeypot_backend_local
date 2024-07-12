import json
from datetime import datetime
from enum import Enum
from typing import List, Dict, Union


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


class Message:
    def __init__(self, is_inbound, from_addr, to_addr, time, medium, body, subject=None):
        self.is_inbound = is_inbound
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.time = datetime.fromtimestamp(time)
        self.medium = MessengerOptions(medium)
        self.body = body

    @classmethod
    def load_from_json(cls, data: Dict[str, Union[str, int]]) -> 'Message':
        return cls(
            is_inbound=data["is_inbound"],
            from_addr=data["from"],
            to_addr=data["to"],
            subject=data["subject"],
            time=data["time"],
            medium=data["medium"],
            body=data["body"]
        )

    def to_json(self):
        return {
            "is_inbound": self.is_inbound,
            "from": self.from_addr,
            "to": self.to_addr,
            "subject": self.subject,
            "time": int(self.time.timestamp()),
            "medium": self.medium.value,
            "body": self.body
        }


class Conversation:
    def __init__(self, unique_scam_id, scam_ids, bait_ids, pause_start, pause_end, already_queued, victim_name):
        self.unique_id = unique_scam_id
        self.scam_ids = scam_ids
        self.bait_ids = bait_ids
        self.pause_start = int(pause_start)
        self.pause_end = int(pause_end)
        self.already_queued = already_queued
        self.victim_name = victim_name
        self.messages: List[Message] = []

    @classmethod
    def load_from_json(cls, json_data: Dict[str, Union[str, int, Dict[str, str]]]) -> 'Conversation':
        conversation = cls(
            unique_scam_id=json_data["unique_id"],
            scam_ids=json_data.get("scam_ids", {}),
            bait_ids=json_data.get("bait_ids", {}),
            pause_start=json_data["pause_start"],
            pause_end=json_data["pause_end"],
            already_queued=json_data["already_queued"],
            victim_name=json_data["victim_name"]
        )

        for message_data in json_data["messages"]:
            message = Message.load_from_json(message_data)
            conversation.add_message(message)

        return conversation

    def add_message(self, message):
        if isinstance(message, Message):
            self.messages.append(message)
        else:
            raise TypeError("Expected a Message instance")

    def to_json(self):
        return json.dumps({
            "unique_id": self.unique_id,
            "scam_ids": self.scam_ids,
            "bait_ids": self.bait_ids,
            "pause_start": int(self.pause_start),
            "pause_end": int(self.pause_end),
            "already_queued": self.already_queued,
            "victim_name": self.victim_name,
            "messages": [message.to_json() for message in self.messages]
        }, indent=4)
