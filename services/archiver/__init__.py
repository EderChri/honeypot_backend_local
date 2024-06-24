from constants import MAIL_ARCHIVE_DIR
import os
import time
from utils.structures import MessengerOptions


def archive(is_inbound, scam_id, response_id, body, medium, subject=None):
    archive_name = f"{scam_id}.txt"

    archive_content = \
        f'\n# {"Inbound" if is_inbound else "Outbound"}\n' \
        f'FROM: {scam_id if is_inbound else response_id}\n' \
        f'TO: {response_id if is_inbound else scam_id}\n' \
        + (f'SUBJECT: {subject}\n' if medium == MessengerOptions.EMAIL else '') \
        + (
            f'TIME: {int(time.time())}\n'
            f'MEDIUM: {medium}\n'
            f'\n{body}\n'
        )

    if not os.path.exists(MAIL_ARCHIVE_DIR):
        os.makedirs(MAIL_ARCHIVE_DIR)

    with open(f"{MAIL_ARCHIVE_DIR}/{archive_name}", "a", encoding="utf8") as f:
        f.write(archive_content)

    # Save conversation history

    history_filename = f"{scam_id}.his"

    if is_inbound:
        his_content = "[scam_start]\n" + body + "\n[scam_end]\n"
    else:
        his_content = "[response_start]\n" + body + "\n[response_end]\n"

    with open(os.path.join(MAIL_ARCHIVE_DIR, history_filename), "a", encoding="utf8") as f:
        f.write(his_content)

    print(f"Archive for {scam_id} completed")
