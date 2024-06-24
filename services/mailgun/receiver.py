from constants import MAIL_SAVE_DIR
from secret import DOMAIN_NAME
import json
import os
from services.archiver import archive
from utils.structures import MessengerOptions


def on_receive(data):
    data_cleaned = {key.strip("'"): value for key, value in data.items()}
    filename = str(data_cleaned.get("timestamp", "")) + ".json"

    res = {"from": str(data_cleaned["sender"]).lower()}

    raw_rec = str(data_cleaned["recipient"])
    if "," in raw_rec:
        for rec in raw_rec.split(","):
            if rec.endswith(DOMAIN_NAME):
                res["bait_email"] = rec
                break
    else:
        res["bait_email"] = raw_rec

    res["title"] = data_cleaned["Subject"]
    res["content"] = data_cleaned["stripped-text"]
    if "stripped-signature" in data_cleaned:
        res["content"] += "\n" + data_cleaned["stripped-signature"]

    if not os.path.exists(MAIL_SAVE_DIR):
        os.makedirs(MAIL_SAVE_DIR)

    with open(f"{MAIL_SAVE_DIR}/{filename}", "w", encoding="utf8") as f:
        json.dump(res, f)

    archive(True, res["from"], res["bait_email"], res["content"], MessengerOptions.EMAIL, res["title"])
