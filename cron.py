import logging
import os
import sys
import traceback

from services import crawler
from constants import IO_TYPE
from services.email.emailprocessor import EmailProcessor
from services.io_utils.factories import LoaderFactory
from utils.common import is_timestamp_in_past
from utils.logging_utils import log
from utils.structures import MessengerOptions


def main(crawl=False):
    if crawl:
        crawler.fetch_all()

    loader = LoaderFactory.get_loader(IO_TYPE)

    try:
        queued_responses = loader.load_schedule_queue()
        for queued_response in queued_responses:
            if is_timestamp_in_past(queued_response):
                scheduled_response_metadata = loader.load_scheduled_response(queued_response)
                match scheduled_response_metadata['switch_medium']:
                    case MessengerOptions.EMAIL:
                        log(f"Handling {scheduled_response_metadata['scam_id']}")
                        processor = EmailProcessor(scheduled_response_metadata['scam_id'], queued_response)
                        processor.handle_email()
    except Exception as e:
        print(e)
        print(traceback.format_exc())


if __name__ == '__main__':
    if os.path.exists("./lock"):
        sys.exit(-1)

    with open("./lock", "w") as f:
        f.write("Running")

    arg_crawl = not ("--no-crawl" in sys.argv)
    main(crawl=False)

    os.remove("./lock")
