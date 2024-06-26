import json
import os
import uuid
from constants import ID_PATH
import logging
from utils.logging_utils import initialise_logging_config


def get_scam_ids():
    if os.path.exists(ID_PATH):
        with open(ID_PATH, 'r', encoding='utf8') as f:
            scam_ids = json.load(f)
    else:
        scam_ids = {}
    return scam_ids


def get_unique_scam_id(scam_id):
    scam_ids = get_scam_ids()

    if scam_id not in scam_ids:
        scam_ids[scam_id] = str(uuid.uuid4())

        with open(ID_PATH, 'w', encoding='utf8') as f:
            json.dump(scam_ids, f)

        initialise_logging_config()
        logging.getLogger().trace(f"New unique scam id {scam_ids[scam_id]} added for {scam_id}")

    return scam_ids[scam_id]


def add_scam_id(unique_scam_id, scam_id):
    scam_ids = get_scam_ids()
    scam_ids[scam_id] = unique_scam_id
    with open(ID_PATH, 'w', encoding='utf8') as f:
        json.dump(scam_ids, f)

    initialise_logging_config()
    logging.getLogger().trace(f"Added {unique_scam_id} to {scam_id}")
