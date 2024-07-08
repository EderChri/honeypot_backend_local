import json
import os

from constants import ARCHIVE_DIR, ID_PATH
from services.io_utils.writer import Writer
from services.io_utils.fileloader import FileLoader
import logging
from utils.logging_utils import initialise_logging_config

class FileWriter(Writer):
    def write_full_data(self, scam_id, archive_content):
        archive_name = f"{scam_id}.json"
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        with open(os.path.join(ARCHIVE_DIR, archive_name), "a", encoding="utf8") as f:
            f.write(json.dumps(archive_content, indent=4))

    def write_history(self, scam_id, body, inbound_flag):
        history_filename = f"{scam_id}.his"

        if inbound_flag:
            his_content = "[scam_start]\n" + body + "\n[scam_end]\n"
        else:
            his_content = "[response_start]\n" + body + "\n[response_end]\n"

        with open(os.path.join(ARCHIVE_DIR, history_filename), "a", encoding="utf8") as f:
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