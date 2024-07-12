import time
from constants import IO_TYPE
from utils.structures import Message, Conversation
from services.io_utils.factories import WriterFactory, LoaderFactory


class Archiver:
    def __init__(self):
        self.writer = WriterFactory.get_writer(IO_TYPE)
        self.loader = LoaderFactory.get_loader(IO_TYPE)

    def archive_message(self, scam_id: str, message: Message, is_unique_id: bool = False):
        if is_unique_id:
            unique_scam_id = scam_id
        else:
            unique_scam_id = self.loader.get_unique_scam_id(scam_id)

        self.writer.add_message(unique_scam_id, message)

    def archive_conversation(self, conversation: Conversation):
        self.writer.write_conversation(conversation)
