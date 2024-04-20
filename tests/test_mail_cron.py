import os
import json
from unittest import mock
from unittest.mock import MagicMock, patch
import pytest
import importlib
from services.responder.replier import Replier

@pytest.fixture
def mocked_email_obj():
    return {
        "content": "Test email content",
        "title": "Test Email",
        "from": "test@example.com",
    }


@pytest.fixture
def mocked_email_path(tmp_path, mocked_email_obj):
    file_path = tmp_path / "test_email.json"
    with open(file_path, "w", encoding="utf8") as f:
        json.dump(mocked_email_obj, f)
    return file_path


@pytest.fixture
def mocked_processor(tmp_path, mocked_email_path):
    with mock.patch("constants.MAIL_TEMPLATE", "../services/mailgun/template.html"), \
        mock.patch("constants.MAIL_SAVE_DIR", tmp_path):
        # Hacky approach, but only viable method I found to force reload of the package to patch constants again
        import services.email.emailprocessor
        importlib.reload(services.email.emailprocessor)
        from services.email.emailprocessor import EmailProcessor

        return EmailProcessor(os.path.basename(mocked_email_path))


def test_add_re_to_subject(mocked_processor):
    subject = "Test Email"
    new_subject = mocked_processor.add_re_to_subject(subject)
    assert new_subject == f"Re: {subject}"


def test_email_processor_init(mocked_processor, mocked_email_path, mocked_email_obj):
    directory, _ = os.path.split(mocked_email_path)
    with mock.patch("constants.MAIL_TEMPLATE", "../services/mailgun/template.html"), \
        mock.patch("constants.MAIL_SAVE_DIR", directory):
        # Hacky approach, but only viable method I found to force reload of the package to patch constants again
        import services.email.emailprocessor
        importlib.reload(services.email.emailprocessor)
        from services.email.emailprocessor import EmailProcessor

        processor = EmailProcessor(os.path.basename(mocked_email_path))
        assert processor.email_filename == os.path.basename(mocked_email_path)
        assert processor.email_path == str(mocked_email_path)
        assert processor.email_obj == mocked_email_obj


def test_handle_crawled_email(mocked_processor):
    mocked_processor.handle_crawled_email = MagicMock()
    mocked_processor.handle_email()
    mocked_processor.handle_crawled_email.assert_called_once()


def test_handle_reply_email(mocked_processor):
    mocked_processor.handle_reply_email = MagicMock()
    mocked_processor.email_obj["bait_email"] = "reply@example.com"
    mocked_processor.handle_email()
    mocked_processor.handle_reply_email.assert_called_once()


@patch("services.mailgun.send_email")
@patch("services.email.emailprocessor.archive")
def test_generate_and_send_reply(mocked_send_email, mocked_archive, mocked_processor):
    mocked_send_email.return_value = True
    mocked_archive.return_value = True
    mocked_processor.generate_and_send_reply(
        MagicMock(),
        "scam@example.com",
        MagicMock(),
        "Test Subject",
        "reply@example.com",
    )
    mocked_send_email.assert_called_once()


@patch("services.email.emailprocessor.shutil.move")
@patch("services.email.emailprocessor.archive")
@patch("services.mailgun.send_email")
def test_generate_and_send_reply_success(
        mocked_send_email, mocked_archive, mocked_move, mocked_processor
):
    mocked_send_email.return_value = True
    mocked_replier = MagicMock()
    mocked_replier.get_reply_by_his = MagicMock(return_value="Expected return value")
    mocked_stored_info = MagicMock()
    mocked_stored_info.username = "Expected Username"
    mocked_processor.generate_and_send_reply(
        mocked_stored_info,
        "scam@example.com",
        mocked_replier,
        "Test Subject",
        "reply@example.com",
    )
    mocked_move.assert_called_once()
    mocked_archive.assert_called_once_with(
        False,
        "scam@example.com",
        "reply@example.com",
        "Test Subject",
        mocked_replier.get_reply_by_his.return_value + f"\nBest,\n{mocked_stored_info.username}",
    )


@patch("services.email.emailprocessor.shutil.move")
@patch("services.email.emailprocessor.archive")
@patch("services.mailgun.send_email")
def test_generate_and_send_reply_failure(
        mocked_send_email, mocked_archive, mocked_move, mocked_processor
):
    mocked_send_email.return_value = False
    mocked_processor.generate_and_send_reply(
        MagicMock(),
        "scam@example.com",
        MagicMock(),
        "Test Subject",
        "reply@example.com",
    )
    mocked_move.assert_not_called()
    mocked_archive.assert_not_called()
