import openai
from constants import SWITCH_DETECTOR_PROMPT_PREFIX, GPT_API_KEY
from services.messenger_switch_detector.structures import DetectionTuple
import instructor

client = openai.OpenAI(
    api_key=GPT_API_KEY
)

client = instructor.patch(client=client)


class MessengerSwitchDetector:
    @staticmethod
    def predict_switch(text: str) -> DetectionTuple:
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
        return messenger
