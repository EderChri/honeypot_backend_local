import os
import pytest
from services.archiver import archive
from unittest.mock import patch
from utils.structures import MessengerOptions

MAIL_ARCHIVE_DIR = "test_mail_archive"


@pytest.fixture
def setup_teardown():
    # Setup: create the directory if it does not exist
    os.makedirs(MAIL_ARCHIVE_DIR, exist_ok=True)
    yield
    # Teardown: remove the directory and its contents
    for filename in os.listdir(MAIL_ARCHIVE_DIR):
        file_path = os.path.join(MAIL_ARCHIVE_DIR, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    os.rmdir(MAIL_ARCHIVE_DIR)


def run_archive_test(is_inbound, scam_id, response_id, body, medium, subject=None):
    archive(is_inbound, scam_id, response_id, body, medium, subject)

    archive_filename = os.path.join(MAIL_ARCHIVE_DIR, f"{scam_id}.txt")
    history_filename = os.path.join(MAIL_ARCHIVE_DIR, f"{scam_id}.his")

    assert os.path.exists(archive_filename)
    assert os.path.exists(history_filename)

    with open(archive_filename, 'r', encoding="utf8") as f:
        content = f.read()
        if subject:
            assert f'SUBJECT: {subject}' in content
        else:
            assert 'SUBJECT:' not in content

    with open(history_filename, 'r', encoding="utf8") as f:
        content = f.read()
        if is_inbound:
            assert "[scam_start]" in content
            assert "[scam_end]" in content
        else:
            assert "[response_start]" in content
            assert "[response_end]" in content


@pytest.mark.parametrize(
    "is_inbound, scam_id, response_id, body, medium, subject", [
        (True, "email_test", "user456", "This is the email body.", MessengerOptions.EMAIL, "Subject Example"),
        (True, "messenger_test", "user457", "This is a WhatsApp message body.", MessengerOptions.WHATSAPP, None),
        (False, "outbound_messenger", "user458", "This is a WhatsApp message body.", MessengerOptions.WHATSAPP, None),
        (False, "outbound_email", "user459", "This is the email body.", MessengerOptions.EMAIL, "Subject Example"),
    ],
    ids=[
        "EMAIL",
        "MESSENGER",
        "OUTBOUND",
        "OUTBOUND EMAIL"
    ]
)
@patch('services.archiver.MAIL_ARCHIVE_DIR', MAIL_ARCHIVE_DIR)
def test_archive(setup_teardown,is_inbound, scam_id, response_id, body, medium, subject):
    run_archive_test(is_inbound, scam_id, response_id, body, medium,
                     subject)
