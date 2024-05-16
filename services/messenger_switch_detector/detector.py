import openai
from constants import SWITCH_DETECTOR_PROMPT_PREFIX
from secret import GPT_API_KEY
from services.messenger_switch_detector.structures import DetectionTuple, MessengerOptions
import instructor
import logging

client = openai.OpenAI(
    api_key=GPT_API_KEY
)

client = instructor.patch(client=client)


class MessengerSwitchDetector:
    @staticmethod
    def predict_switch(text: str) -> DetectionTuple:
        try:
            messenger = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_model=DetectionTuple,
                messages=[
                    {
                        "role": "user",
                        "content": SWITCH_DETECTOR_PROMPT_PREFIX + "\n" + text
                    }
                ]
            )
        except Exception as e:
            messenger = DetectionTuple(switch=False, messenger=MessengerOptions.OTHER)
            logging.exception("An error occurred in messenger_switch_detector: %s", str(e))
        finally:
            return messenger
