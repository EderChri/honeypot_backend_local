import time
from constants import IO_TYPE
from utils.structures import MessengerOptions
from utils.storage_utils import get_unique_scam_id
from services.io_utils.writer_factory import WriterFactory


class Archiver:
    def __init__(self):
        self.writer = WriterFactory.get_writer(IO_TYPE)

    def archive(self, is_inbound, scam_id, response_id, body, medium, subject=None):
        unique_scam_id = get_unique_scam_id(scam_id)

        archive_content = {
            "direction": "Inbound" if is_inbound else "Outbound",
            "from": scam_id if is_inbound else response_id,
            "to": response_id if is_inbound else scam_id,
            "subject": subject if medium == MessengerOptions.EMAIL else None,
            "time": int(time.time()),
            "medium": medium,
            "body": body
        }

        self.writer.write_full_data(unique_scam_id, archive_content)
        self.writer.write_history(unique_scam_id, body, is_inbound)
