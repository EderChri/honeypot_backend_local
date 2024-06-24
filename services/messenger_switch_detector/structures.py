from pydantic import BaseModel, Field

from utils.structures import MessengerOptions


class DetectionTuple(BaseModel):
    switch: bool
    messenger: MessengerOptions = Field(
        description="Correctly assign one of the messengers"
    )
