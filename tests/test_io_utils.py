import json

import pytest
from unittest import mock
from services.io_utils.fileloader import FileLoader
from services.io_utils.filewriter import FileWriter
from utils.structures import Conversation, Message, MessengerOptions


@pytest.fixture
def filewriter():
    return FileWriter()


@pytest.fixture
def fileloader():
    return FileLoader()


def test_get_scam_ids(fileloader):
    with mock.patch('os.path.exists', return_value=True):
        with mock.patch('builtins.open', mock.mock_open(read_data='{"test_id": "1234"}')):
            scam_ids = fileloader.get_scam_ids()
            assert scam_ids == {"test_id": "1234"}

    with mock.patch('os.path.exists', return_value=False):
        scam_ids = fileloader.get_scam_ids()
        assert scam_ids == {}


def test_get_unique_scam_id(fileloader):
    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={}):
        with mock.patch('builtins.open', mock.mock_open()):
            with mock.patch('json.dump') as mock_json_dump:
                with mock.patch('utils.logging_utils.log'):
                    unique_id = fileloader.get_unique_scam_id('test_id')
                    assert unique_id is not None
                    mock_json_dump.assert_called_once()

    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={'test_id': '1234'}):
        with mock.patch('utils.logging_utils.log'):
            unique_id = fileloader.get_unique_scam_id('test_id')
            assert unique_id == '1234'


def test_write_conversation(filewriter):
    conversation = Conversation("test_id", ["test_scam"], {}, 0, 0, True, "test")
    with mock.patch('os.makedirs'), mock.patch('builtins.open', mock.mock_open()) as mock_file:
        filewriter.write_conversation(conversation)
        # Combine all write calls from json dumps into a single string
        written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)

        # Assert that the final written data matches the expected JSON output
        mock_file().write.assert_called()
        assert written_data == json.dumps(conversation.to_json(), indent=4)


def test_write_history(filewriter):
    conversation = Conversation("test_id", ["test_scam"], ["test_victim"], 0, 0, True, "test")
    conversation.add_message(Message(True, "from", "to", 0, MessengerOptions.EMAIL, "test_body", "test_subject"))
    conversation.add_message(Message(False, "from", "to", 0, MessengerOptions.EMAIL, "test_body", "test_subject"))
    with mock.patch('builtins.open', mock.mock_open()) as mock_file:
        filewriter.write_history(conversation)

        expected_calls = [
            mock.call().write("[scam_start]\n" + "test_body" + "\n[scam_end]\n"),
            mock.call().write("[response_start]\n" + "test_body" + "\n[response_end]\n")
        ]
        mock_file.assert_has_calls(expected_calls, any_order=False)


def test_add_scam_id(filewriter):
    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={}):
        with mock.patch('builtins.open', mock.mock_open()):
            with mock.patch('json.dump') as mock_json_dump:
                filewriter.add_scam_id('unique_id', 'test_scam')
                mock_json_dump.assert_called_once()
