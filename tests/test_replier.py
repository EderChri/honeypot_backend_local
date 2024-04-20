import pytest
from unittest.mock import MagicMock
from services.responder import MailReplier, WhatsAppReplier, InstagramReplier, FacebookReplier


@pytest.fixture
def mock_gen_text(monkeypatch):
    mock = MagicMock(return_value="Mocked reply")
    monkeypatch.setattr("responder.replier.gen_text", mock)
    return mock


@pytest.mark.parametrize("replier_cls", [MailReplier, WhatsAppReplier, InstagramReplier, FacebookReplier])
def test_replier(replier_cls, mock_gen_text):
    replier = replier_cls()
    reply = replier.get_reply("Test content")
    assert reply == "Mocked reply"
    mock_gen_text.assert_called_once_with(f"{replier.prompt_prefix}\nTest content", None)
