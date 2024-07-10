import pytest
from unittest.mock import patch
from services.messenger_switch_detector.detector import MessengerSwitchDetector
from services.messenger_switch_detector.structures import DetectionTuple, MessengerOptions
from constants import SWITCH_DETECTOR_PROMPT_PREFIX


@pytest.fixture
def mock_openai_client():
    with patch("services.messenger_switch_detector.detector.client") as mock_client:
        yield mock_client


def test_predict_switch(mock_openai_client):
    expected_response = DetectionTuple(switch=True, messenger=MessengerOptions.WHATSAPP)
    mock_openai_client.chat.completions.create.return_value = expected_response

    input_text = "Sample text"
    result = MessengerSwitchDetector.predict_switch(input_text)

    assert result == expected_response
    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="gpt-3.5-turbo",
        response_model=DetectionTuple,
        messages=[
            {
                "role": "user",
                "content": f"{SWITCH_DETECTOR_PROMPT_PREFIX}\n{input_text}"
            }
        ]
    )


def test_predict_switch_error(mock_openai_client, caplog):
    mock_openai_client.chat.completions.create.side_effect = Exception("Sample error")

    input_text = "Sample text"

    result = MessengerSwitchDetector.predict_switch(input_text)

    assert result.switch == False  # Assuming DetectionTuple has attributes switch and messenger
    assert result.messenger == MessengerOptions.OTHER

    # Verify that the exception was logged
    assert "An error occurred in messenger_switch_detector" in caplog.text
    assert "Sample error" in caplog.text
