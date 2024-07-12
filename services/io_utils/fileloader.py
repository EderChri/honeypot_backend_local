import json
import os
import uuid

import ijson as ijson

from constants import ID_PATH, ARCHIVE_DIR, MAIL_TEMPLATE, QUEUE_DIR
from services.io_utils.interfaces import LoaderInterface
import logging
from utils.logging_utils import initialise_logging_config
from utils.structures import Conversation


class FileLoader(LoaderInterface):
    def load_schedule_queue(self):
        try:
            queue = os.listdir(QUEUE_DIR)
        except FileNotFoundError:
            logging.getLogger().error("Error: Queue directory not found.")
            return None
        return queue

    def load_scheduled_response(self, filename):
        try:
            with open(os.path.join(QUEUE_DIR, filename), 'r', encoding='utf8') as f:
                schedule_data = json.load(f)
            return schedule_data
        except FileNotFoundError:
            logging.getLogger().error(f"Error: File {filename}.json not found in queue.")
            return None

    def load_conversation(self, scam_id, is_unique_id=False):
        if is_unique_id:
            unique_scam_id = scam_id
        else:
            unique_scam_id = self.get_unique_scam_id(scam_id)
        try:
            archive_name = f"{unique_scam_id}.json"
            with open(os.path.join(ARCHIVE_DIR, archive_name), 'r', encoding='utf8') as f:
                scam_data = json.load(f)
        except FileNotFoundError:
            logging.getLogger().error(f"Error: File {unique_scam_id}.json not found.")
            return None
        return Conversation.load_from_json(scam_data)

    def load_history(self, scam_id, is_unique_id=False):
        if is_unique_id:
            unique_scam_id = scam_id
        else:
            unique_scam_id = self.get_unique_scam_id(scam_id)
        try:
            with open(os.path.join(ARCHIVE_DIR, unique_scam_id + ".his"), "r", encoding="utf8") as f:
                content = f.read()
        except FileNotFoundError:
            logging.getLogger().error(f"Error: File {unique_scam_id}.json not found.")
            return None
        return content

    def get_scam_ids(self):
        if os.path.exists(ID_PATH):
            with open(ID_PATH, 'r', encoding='utf8') as f:
                scam_ids = json.load(f)
        else:
            scam_ids = {}
        return scam_ids

    def get_unique_scam_id(self, scam_id) -> str:
        scam_ids = self.get_scam_ids()

        if scam_id not in scam_ids:
            unique_scam_id = str(uuid.uuid4())
            # Import here to avoid loading circular dependencies
            from services.io_utils.filewriter import FileWriter
            writer = FileWriter()
            writer.add_scam_id(unique_scam_id, scam_id)
            scam_ids[scam_id] = unique_scam_id

            initialise_logging_config()
            logging.getLogger().trace(f"New unique scam id {scam_ids[scam_id]} added for {scam_id}")

        return scam_ids[scam_id]

    def scam_exists(self, scam_id) -> bool:
        unique_scam_id = self.get_unique_scam_id(scam_id)
        archive_name = f"{unique_scam_id}.json"
        return os.path.exists(os.path.join(ARCHIVE_DIR, archive_name))

    def load_mail_template(self):
        with open(MAIL_TEMPLATE, "r") as f:
            template = f.read()
        return template

    def check_if_address_exists(self, target_address):
        for filename in os.listdir(ARCHIVE_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(ARCHIVE_DIR, filename)
                with open(file_path, 'r') as file:
                    try:
                        parser = ijson.parse(file)
                        for prefix, event, value in parser:
                            if (prefix, event) == ('bait_ids.Email', 'string') and value == target_address:
                                return True
                    except Exception as e:
                        logging.getLogger().error(f"Error parsing JSON in file: {file_path}, error: {e}")
        return False

        