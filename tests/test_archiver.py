import json
import os
import pytest
from services.archiver import Archiver
from unittest.mock import patch
from utils.structures import MessengerOptions
from utils.storage_utils import get_unique_scam_id

ARCHIVE_DIR = "test_archive"


@pytest.fixture
def setup_teardown():
    # Setup: create the directory if it does not exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    yield
    # Teardown: remove the directory and its contents
    for filename in os.listdir(ARCHIVE_DIR):
        file_path = os.path.join(ARCHIVE_DIR, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    os.rmdir(ARCHIVE_DIR)


def run_archive_test(is_inbound, scam_id, response_id, body, medium, subject=None):
    Archiver.archive(is_inbound, scam_id, response_id, body, medium, subject)

    unique_scam_id = get_unique_scam_id(scam_id)
    archive_filename = os.path.join(ARCHIVE_DIR, f"{unique_scam_id}.json")
    history_filename = os.path.join(ARCHIVE_DIR, f"{unique_scam_id}.his")

    assert os.path.exists(archive_filename)
    assert os.path.exists(history_filename)

    with open(archive_filename, 'r', encoding="utf8") as f:
        content = json.load(f)
        if subject:
            assert f'Subject Example' in content["subject"]
        else:
            assert content["subject"] is None

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
@patch('services.archiver.archiver.ARCHIVE_DIR', ARCHIVE_DIR)
def test_archive(setup_teardown,is_inbound, scam_id, response_id, body, medium, subject):
    run_archive_test(is_inbound, scam_id, response_id, body, medium,
                     subject)
