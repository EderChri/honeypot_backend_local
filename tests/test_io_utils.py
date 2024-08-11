import json

from unittest import mock


def test_get_scam_ids(loader):
    with mock.patch('os.path.exists', return_value=True):
        with mock.patch('builtins.open', mock.mock_open(read_data='{"test_id": "1234"}')):
            scam_ids = loader.get_scam_ids()
            assert scam_ids == {"test_id": "1234"}

    with mock.patch('os.path.exists', return_value=False):
        scam_ids = loader.get_scam_ids()
        assert scam_ids == {}


def test_get_unique_scam_id(loader):
    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={}):
        with mock.patch('builtins.open', mock.mock_open()):
            with mock.patch('json.dump') as mock_json_dump:
                with mock.patch('utils.logging_utils.log'):
                    unique_id = loader.get_unique_scam_id('test_id')
                    assert unique_id is not None
                    mock_json_dump.assert_called_once()

    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={'test_id': '1234'}):
        with mock.patch('utils.logging_utils.log'):
            unique_id = loader.get_unique_scam_id('test_id')
            assert unique_id == '1234'


def test_write_conversation(writer, mocked_conversation, mocked_history):
    with mock.patch('os.makedirs'), mock.patch('builtins.open', mock.mock_open()) as mock_file:
        writer.write_conversation(mocked_conversation)
        # Combine all write calls from json dumps into a single string
        written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)

        # Assert that the final written data matches the expected JSON output
        mock_file().write.assert_called()
        assert written_data == f"{json.dumps(mocked_conversation.to_json(), indent=4)}{mocked_history}"


def test_write_history(writer, mocked_conversation):
    with mock.patch('builtins.open', mock.mock_open()) as mock_file:
        writer.write_history(mocked_conversation)

        expected_calls = [
            mock.call().write("[scam_start]\n" + "test_body" + "\n[scam_end]\n"),
            mock.call().write("[response_start]\n" + "test_body" + "\n[response_end]\n")
        ]
        mock_file.assert_has_calls(expected_calls, any_order=False)


def test_add_scam_id(writer):
    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={}):
        with mock.patch('builtins.open', mock.mock_open()):
            with mock.patch('json.dump') as mock_json_dump:
                writer.add_scam_id('unique_id', 'test_scam')
                mock_json_dump.assert_called_once()
