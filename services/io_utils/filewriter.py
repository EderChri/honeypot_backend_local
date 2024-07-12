import json
import os
import shutil

from constants import ARCHIVE_DIR, ID_PATH, HANDLED_DIR, QUEUE_DIR
from services.io_utils.interfaces import WriterInterface
from services.io_utils.fileloader import FileLoader
import logging
from utils.logging_utils import initialise_logging_config
from utils.structures import Message, Conversation


class FileWriter(WriterInterface):
    def write_conversation(self, conversation: Conversation):
        archive_name = f"{conversation.unique_id}.json"
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        with open(os.path.join(ARCHIVE_DIR, archive_name), "w", encoding="utf8") as f:
            f.write(conversation.to_json())
        self.write_history(conversation)

    def add_message(self, unique_scam_id: str, message: Message):
        conversation = FileLoader().load_conversation(unique_scam_id, is_unique_id=True)
        if conversation is None:
            logging.getLogger().error(f"Error: Conversation for {unique_scam_id} not found.")
            return
        conversation.add_message(message)
        self.write_conversation(conversation)

    def write_history(self, conversation: Conversation):
        history_filename = f"{conversation.unique_id}.his"

        with open(os.path.join(ARCHIVE_DIR, history_filename), "w", encoding="utf8") as f:
            for message in conversation.messages:
                if message.is_inbound:
                    his_content = "[scam_start]\n" + message.body + "\n[scam_end]\n"
                else:
                    his_content = "[response_start]\n" + message.body + "\n[response_end]\n"

                f.write(his_content)

    def write_schedule(self):
        raise NotImplementedError

    def add_scam_id(self, unique_scam_id, scam_id):
        scam_ids = FileLoader().get_scam_ids()
        scam_ids[scam_id] = unique_scam_id
        with open(ID_PATH, 'w', encoding='utf8') as f:
            json.dump(scam_ids, f)

        initialise_logging_config()
        logging.getLogger().trace(f"Added {unique_scam_id} to {scam_id}")

    def move_from_queued_to_handled(self, conversation, queued_response):
        os.makedirs(HANDLED_DIR, exist_ok=True)
        shutil.move(os.path.join(QUEUE_DIR, queued_response),
                    os.path.join(HANDLED_DIR, queued_response))
        conversation.already_queued = False
        self.write_conversation(conversation)
        initialise_logging_config()
        logging.getLogger().trace(f"Moved {conversation.unique_id} to handled")

    def remove_scam_from_queue(self, scam_id):
        unique_scam_id = FileLoader().get_unique_scam_id(scam_id)
        os.remove(os.path.join(QUEUE_DIR, f"{unique_scam_id}.json"))
        initialise_logging_config()
        logging.getLogger().trace(f"Removed {scam_id} from queue")

    def add_scam_to_queue(self, scam_id, next_response_time, medium, switch_medium):
        unique_scam_id = FileLoader().get_unique_scam_id(scam_id)
        os.makedirs(QUEUE_DIR, exist_ok=True)
        with open(os.path.join(QUEUE_DIR, f"{next_response_time}.json"), "w", encoding="utf8") as f:
            f.write(json.dumps({"scam_id": unique_scam_id, "medium": medium, "switch_medium": switch_medium}))
        initialise_logging_config()
        logging.getLogger().trace(f"Added {scam_id} to queue")
