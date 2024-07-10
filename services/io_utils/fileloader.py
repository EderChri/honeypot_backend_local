import json
import os
import uuid
from constants import ID_PATH, MAIL_ADDR_PATH
from services.io_utils.loader import Loader
import logging
from utils.logging_utils import initialise_logging_config


class FileLoader(Loader):
    def load_schedule(self, timestamp):
        pass

    def load_scam_data(self, scam_id):
        unique_scam_id = self.get_unique_scam_id(scam_id)
        with open(f"{unique_scam_id}.json", 'r', encoding='utf8') as f:
            scam_data = json.load(f)
        return scam_data

    def load_history(self, id):
        pass

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
