import json
import os
import shutil

from constants import ARCHIVE_DIR, ID_PATH, HANDLED_DIR, QUEUE_DIR
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

    def move_from_queued_to_handled(self, scam_id):
        unique_scam_id = FileLoader().get_unique_scam_id(scam_id)
        os.makedirs(HANDLED_DIR, exist_ok=True)
        shutil.move(os.path.join(QUEUE_DIR, f"{unique_scam_id}.json"),
                    os.path.join(HANDLED_DIR, f"{unique_scam_id}.json"))
        initialise_logging_config()
        logging.getLogger().trace(f"Moved {scam_id} to handled")

    def remove_scam_from_queue(self, scam_id):
        unique_scam_id = FileLoader().get_unique_scam_id(scam_id)
        os.remove(os.path.join(QUEUE_DIR, f"{unique_scam_id}.json"))
        initialise_logging_config()
        logging.getLogger().trace(f"Removed {scam_id} from queue")
