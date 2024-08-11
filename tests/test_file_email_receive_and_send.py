import datetime
import os
from unittest.mock import patch, Mock, MagicMock

from secret import API_BASE_URL, API_KEY
from services.email.emailprocessor import EmailProcessor
from services.io_utils import FileLoader
from services.messengers import MessengerFactory
from utils.common import is_timestamp_in_past
from utils.structures import MessengerOptions


@patch('services.io_utils.filewriter.ARCHIVE_DIR', new='data/archive')
def test_receive_email_write_json_and_hist(post_request, setup_and_cleanup):
    with patch('services.io_utils.filewriter.ARCHIVE_DIR', new='data/archive'), \
            patch('services.io_utils.fileloader.FileLoader.get_unique_scam_id',
                  return_value='test_scam_id'), \
            patch('services.io_utils.fileloader.FileLoader.load_mail_template',
                  return_value='test_template') as mock_load_mail_template:
        MessengerFactory.get_messenger(MessengerOptions.EMAIL).receive_message(post_request)

        assert os.path.exists('data/archive/test_scam_id.json')
        assert os.path.exists('data/archive/test_scam_id.his')
        mock_load_mail_template.assert_called_once()


def test_receive_email_queue_response(post_request, setup_and_cleanup):
    timestamp = datetime.datetime.now()
    with patch('services.io_utils.filewriter.ARCHIVE_DIR', new='data/archive'), \
            patch('services.io_utils.fileloader.FileLoader.get_unique_scam_id',
                  return_value='test_scam_id'), \
            patch('services.io_utils.fileloader.FileLoader.load_mail_template',
                  return_value='test_template') as mock_load_mail_template, \
            patch('services.io_utils.filewriter.QUEUE_DIR', new='data/queued'), \
            patch('services.scheduler.simple_scheduler.SimpleScheduler.get_next_response_time', return_value=timestamp):
        MessengerFactory.get_messenger(MessengerOptions.EMAIL).receive_message(post_request)
        assert os.path.exists(f'data/queued/{timestamp.timestamp()}.json')
        mock_load_mail_template.assert_called_once()


def test_send_email_from_queue(post_request, setup_and_cleanup):
    timestamp = datetime.datetime.now()

    mock_response = Mock()
    mock_response.text = "Queued."

    with patch('services.io_utils.filewriter.ARCHIVE_DIR', new='data/archive'), \
            patch('services.io_utils.fileloader.FileLoader.get_unique_scam_id', return_value='test_scam_id'), \
            patch('services.io_utils.fileloader.FileLoader.load_mail_template',
                  return_value='test_template') as mock_load_mail_template, \
            patch('services.io_utils.filewriter.QUEUE_DIR', new='data/queued'), \
            patch('services.io_utils.fileloader.QUEUE_DIR', new='data/queued'), \
            patch('requests.post', return_value=mock_response) as mock_post, \
            patch('services.email.emailprocessor.names.get_first_name', return_value='test'), \
            patch('services.scheduler.simple_scheduler.SimpleScheduler.get_next_response_time', return_value=timestamp):

        mocked_replier = MagicMock()
        mocked_replier.get_reply_by_his = MagicMock(return_value="Expected return value")

        MessengerFactory.get_messenger(MessengerOptions.EMAIL).receive_message(post_request)
        loader = FileLoader()
        queued_responses = loader.load_schedule_queue()

        for queued_response in queued_responses:
            if is_timestamp_in_past(queued_response):
                scheduled_response_metadata = loader.load_scheduled_response(queued_response)
                if scheduled_response_metadata['switch_medium'] == MessengerOptions.EMAIL:
                    processor = EmailProcessor(scheduled_response_metadata['scam_id'], queued_response)
                    processor.handle_email()

        mock_post.assert_called_once_with(
            f"https://api.mailgun.net/v3/{API_BASE_URL}/messages",
            auth=("api", API_KEY),
            data={
                "from": "test <victim@test.test>",
                "to": ["scam@test.test"],
                "subject": "Test Subject",
                "html": 'test_template'.replace("{{{content}}}", "Expected return value").replace("\n", "<br>")
            }
        )
