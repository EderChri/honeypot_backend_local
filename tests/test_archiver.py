import pytest
from unittest.mock import Mock, patch
from services.archiver import Archiver
from utils.structures import Message, Conversation


@pytest.fixture
def mock_writer():
    return Mock()


@pytest.fixture
def mock_loader():
    return Mock()


@pytest.fixture
def archiver(mock_writer, mock_loader):
    with patch('services.io_utils.factories.WriterFactory.get_writer', return_value=mock_writer):
        with patch('services.io_utils.factories.LoaderFactory.get_loader', return_value=mock_loader):
            return Archiver()


def test_archive_message_with_unique_id(archiver, mock_writer):
    scam_id = "scam123"
    message = Message(is_inbound=True, from_addr="sender", to_addr="receiver", time=1625247600, medium="Email",
                      body="Test message")

    archiver.archive_message(scam_id, message, is_unique_id=True)

    mock_writer.add_message.assert_called_once_with(scam_id, message)


def test_archive_message_without_unique_id(archiver, mock_loader, mock_writer):
    scam_id = "scam123"
    message = Message(is_inbound=True, from_addr="sender", to_addr="receiver", time=1625247600, medium="Email",
                      body="Test message")
    unique_scam_id = "unique_scam_id"

    mock_loader.get_unique_scam_id.return_value = unique_scam_id

    archiver.archive_message(scam_id, message, is_unique_id=False)

    mock_loader.get_unique_scam_id.assert_called_once_with(scam_id)
    mock_writer.add_message.assert_called_once_with(unique_scam_id, message)


def test_archive_conversation(archiver, mock_writer):
    conversation = Conversation(unique_scam_id="conv123", scam_ids={}, victim_ids={}, pause_start=0, pause_end=0,
                                already_queued=False, victim_name="victim")

    archiver.archive_conversation(conversation)

    mock_writer.write_conversation.assert_called_once_with(conversation)
