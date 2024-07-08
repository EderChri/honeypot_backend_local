import json
import pytest
from unittest import mock
from services.io_utils.fileloader import FileLoader
from services.io_utils.filewriter import FileWriter


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
                with mock.patch('utils.logging_utils.initialise_logging_config'), mock.patch('logging.getLogger'):
                    unique_id = fileloader.get_unique_scam_id('test_id')
                    assert unique_id is not None
                    mock_json_dump.assert_called_once()

    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={'test_id': '1234'}):
        with mock.patch('utils.logging_utils.initialise_logging_config'), mock.patch('logging.getLogger'):
            unique_id = fileloader.get_unique_scam_id('test_id')
            assert unique_id == '1234'


def test_write_full_data(filewriter):
    scam_id = "test_scam"
    content = {"key": "value"}
    with mock.patch('os.makedirs'), mock.patch('builtins.open', mock.mock_open()) as mock_file:
        filewriter.write_full_data(scam_id, content)
        mock_file().write.assert_called_once_with(json.dumps(content, indent=4))


def test_write_history(filewriter):
    scam_id = "test_scam"
    body = "test body"
    with mock.patch('builtins.open', mock.mock_open()) as mock_file:
        filewriter.write_history(scam_id, body, inbound_flag=True)
        mock_file().write.assert_called_once_with("[scam_start]\n" + body + "\n[scam_end]\n")

    with mock.patch('builtins.open', mock.mock_open()) as mock_file:
        filewriter.write_history(scam_id, body, inbound_flag=False)
        mock_file().write.assert_called_once_with("[response_start]\n" + body + "\n[response_end]\n")


def test_add_scam_id(filewriter):
    with mock.patch('services.io_utils.fileloader.FileLoader.get_scam_ids', return_value={}):
        with mock.patch('builtins.open', mock.mock_open()):
            with mock.patch('json.dump') as mock_json_dump:
                filewriter.add_scam_id('unique_id', 'test_scam')
                mock_json_dump.assert_called_once()
