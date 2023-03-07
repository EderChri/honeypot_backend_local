from typing import Optional

from secret import ADDR_SOL_PATH
import json
import os
import names
from collections import namedtuple

StoredInfo = namedtuple("StoredInfo", ["addr", "to", "sol", "username", "lastname", "classification", "used_templates"])

if not os.path.exists(os.path.dirname(ADDR_SOL_PATH)):
    os.makedirs(os.path.dirname(ADDR_SOL_PATH))

if not os.path.exists(ADDR_SOL_PATH):
    with open(ADDR_SOL_PATH, "w", encoding="utf8") as f:
        json.dump({}, f)


def addr_exists(addr) -> bool:
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    if addr in d:
        return True
    return False


def scam_exists(addr) -> bool:
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    for bait in d:
        if d[bait]["to"] == addr:
            return True
    return False


def update_used_templates(current_template, addr):

    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        record = json.load(f)

    record[addr]['used_templates'].append(current_template)

    with open(ADDR_SOL_PATH, "w") as f:
        json.dump(record, f)





def store_addr(addr, scam_email, sol_name, classification):
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    replierGender = "all"
    if (sol_name == "OldWoman"):
        replierGender = "female"
    elif (sol_name == "ProfitFocusedMan"):
        replierGender = "male"

    d[addr] = {
        "to": scam_email,
        "sol": sol_name,
        "username": names.get_first_name(gender = replierGender),
        "lastname": names.get_last_name(),
        "classification": classification,
        "used_templates": []
    }

    with open(ADDR_SOL_PATH, "w", encoding="utf8") as f:
        json.dump(d, f, indent=4)


def get_stored_info(addr, scam_email) -> Optional[StoredInfo]:
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    obj = None

    if addr not in d:
        for bait in d:
            if d[bait]["to"] == scam_email:
                obj = d[bait]
                addr = bait
                break
    else:
        obj = d[addr]
    if obj is None:
        return None
    return StoredInfo(addr, obj["to"], obj["sol"], obj["username"], obj["lastname"], obj["classification"], obj["used_templates"])
