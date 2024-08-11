import importlib
from unittest import mock
from unittest.mock import patch, MagicMock

import pytest
import os

from werkzeug.datastructures import ImmutableMultiDict

import constants
from services.archiver import Archiver
from services.email.emailprocessor import EmailProcessor
from services.io_utils import FileWriter, FileLoader
from services.scheduler import SchedulerFactory
from utils.structures import Conversation, Message, MessengerOptions


@pytest.fixture
def setup_and_cleanup():
    directories = ['data/archive', 'data/queued', 'data/handled']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    yield

    for directory in directories:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(directory)
    os.rmdir('data')


@pytest.fixture
def post_request():
    return ImmutableMultiDict([
        ('timestamp', '1618109761'),
        ('sender', 'scam@test.test'),
        ('recipient', 'victim@test.test'),
        ('Subject', 'Test Subject'),
        ('stripped-text', 'Test content'),
        ('stripped-signature', 'Test signature')
    ])


@pytest.fixture
def mock_openai_client():
    with patch("services.messenger_switch_detector.detector.client") as mock_client:
        yield mock_client


@pytest.fixture
def mocked_writer():
    return MagicMock()


@pytest.fixture
def mocked_loader():
    return MagicMock()


@pytest.fixture
def writer():
    return FileWriter()


@pytest.fixture
def loader():
    return FileLoader()


@pytest.fixture
def mocked_empty_conversation():
    return Conversation("unique_scam_id", {MessengerOptions.EMAIL: "test_id"},
                        {MessengerOptions.EMAIL: "test_victim_id"}, 0, 0, False, "test_victim")


@pytest.fixture
def mocked_conversation(mocked_empty_conversation):
    mocked_empty_conversation.add_message(
        Message(True, "from", "to", 0, MessengerOptions.EMAIL, "test_body", "test_subject"))
    mocked_empty_conversation.add_message(
        Message(False, "from", "to", 0, MessengerOptions.EMAIL, "test_body", "test_subject"))
    return mocked_empty_conversation


@pytest.fixture
def mocked_crawled_conversation(mocked_empty_conversation):
    mocked_empty_conversation.add_message(
        Message(True, "from", constants.CRAWLER_FLAG, 0, MessengerOptions.EMAIL, "test_body", "test_subject"))
    return mocked_empty_conversation


@pytest.fixture
def mocked_history(mocked_conversation):
    his_content = ""
    for message in mocked_conversation.messages:
        if message.is_inbound:
            his_content += "[scam_start]\n" + message.body + "\n[scam_end]\n"
        else:
            his_content += "[response_start]\n" + message.body + "\n[response_end]\n"
    return his_content


@pytest.fixture
def mocked_queued_response(setup_and_cleanup):
    with open('data/queued/0.json', 'w') as _:
        pass
    return 'data/queued/0.json'


@pytest.fixture
def mocked_mail_template():
    template = """
    <html lang="en">
    <body>
    <div>
        {{{{content}}}}
    </div>
    </body>

    <style>
        body {
            width: 100%;
        }

        div {
            font-size: 20px;
            font-family: Georgia, sans-serif;
            max-width: 30rem;
            word-break: break-word;
        }
    </style>
    </html>
    """
    return template


@pytest.fixture
def mocked_processor(setup_and_cleanup, mocked_conversation, mocked_mail_template, mocked_queued_response):
    with mock.patch("services.io_utils.fileloader.FileLoader.load_mail_template", return_value=mocked_mail_template), \
            mock.patch("services.io_utils.fileloader.FileLoader.load_conversation", return_value=mocked_conversation):
        return EmailProcessor(mocked_conversation.unique_id, mocked_queued_response)


@pytest.fixture
def simple_scheduler():
    return SchedulerFactory.get_scheduler(constants.SCHEDULER_TYPE)


@pytest.fixture
def mock_gen_text():
    with patch('services.responder.replier.gen_text') as mock:
        mock.return_value = "Mocked reply"
        yield mock


@pytest.fixture
def archiver(mocked_writer, mocked_loader):
    with patch('services.io_utils.factories.WriterFactory.get_writer', return_value=mocked_writer):
        with patch('services.io_utils.factories.LoaderFactory.get_loader', return_value=mocked_loader):
            return Archiver()