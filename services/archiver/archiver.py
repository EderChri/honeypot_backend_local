import os
import time
import json
from constants import ARCHIVE_DIR
from utils.structures import MessengerOptions
from utils.storage_utils import get_unique_scam_id


class Archiver:
    @staticmethod
    def archive(is_inbound, scam_id, response_id, body, medium, subject=None):
        unique_scam_id = get_unique_scam_id(scam_id)
        archive_name = f"{unique_scam_id}.json"

        archive_content = {
            "direction": "Inbound" if is_inbound else "Outbound",
            "from": scam_id if is_inbound else response_id,
            "to": response_id if is_inbound else scam_id,
            "subject": subject if medium == MessengerOptions.EMAIL else None,
            "time": int(time.time()),
            "medium": medium,
            "body": body
        }

        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        with open(os.path.join(ARCHIVE_DIR, archive_name), "a", encoding="utf8") as f:
            f.write(json.dumps(archive_content, indent=4))

        Archiver.save_history(is_inbound, unique_scam_id, body)

        print(f"Archive for {unique_scam_id} completed")

    @staticmethod
    def save_history(is_inbound, unique_scam_id, body):
        history_filename = f"{unique_scam_id}.his"

        if is_inbound:
            his_content = "[scam_start]\n" + body + "\n[scam_end]\n"
        else:
            his_content = "[response_start]\n" + body + "\n[response_end]\n"

        with open(os.path.join(ARCHIVE_DIR, history_filename), "a", encoding="utf8") as f:
            f.write(his_content)
