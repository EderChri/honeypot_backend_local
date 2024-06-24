import os
import json
import shutil
import traceback

from constants import MAIL_SAVE_DIR, MAIL_HANDLED_DIR
from services import solution_manager, responder, mailgun
from services.archiver import archive
from utils.structures import MessengerOptions


class EmailProcessor:
    def __init__(self, email_filename):
        self.email_filename = email_filename
        self.email_path = os.path.join(MAIL_SAVE_DIR, email_filename)
        with open(self.email_path, "r", encoding="utf8") as f:
            self.email_obj = json.load(f)

    @staticmethod
    def add_re_to_subject(subject):
        if not subject.startswith("Re:"):
            subject = "Re: " + subject
        return subject

    def handle_crawled_email(self, scam_email, text, subject):
        if solution_manager.scam_exists(scam_email):
            print("This crawled email has been replied, ignoring")
            os.remove(self.email_path)
            return

        archive(True, scam_email, "CRAWLER", text, MessengerOptions.EMAIL, self.email_obj["title"])

        print("This email is just crawled, using random replier")
        replier = responder.get_replier_randomly()
        bait_email = solution_manager.gen_new_addr(scam_email, replier.name)
        stored_info = solution_manager.get_stored_info(bait_email, scam_email)

        if stored_info is None:
            print(f"Cannot find replier for {bait_email}")
            os.remove(self.email_path)
            return

        self.generate_and_send_reply(stored_info, scam_email, replier, subject, bait_email)

    def handle_reply_email(self, scam_email, subject):
        bait_email = self.email_obj["bait_email"]
        stored_info = solution_manager.get_stored_info(bait_email, scam_email)

        if stored_info is None:
            print(f"Cannot find replier for {bait_email}")
            os.remove(self.email_path)
            return

        print(f"Found selected replier {stored_info.sol}")
        replier = responder.get_replier_by_name(stored_info.sol)

        if replier is None:
            print("Replier Sol_name not found")
            os.remove(self.email_path)
            return

        self.generate_and_send_reply(stored_info, scam_email, replier, subject, bait_email)

    def generate_and_send_reply(self, stored_info, scam_email, replier, subject, bait_email):
        try:
            res_text = replier.get_reply_by_his(scam_email)
        except Exception as e:
            print("GENERATING ERROR")
            print(e)
            print(traceback.format_exc())
            print("Due to CUDA Error, stopping whole sequence")
            return

        # Add Signature
        res_text += f"\nBest,\n{stored_info.username}"

        send_result = mailgun.send_email(stored_info.username, stored_info.addr, scam_email, subject, res_text)
        if send_result:
            print(f"Successfully sent response to {scam_email}")

            # Move to queued
            if not os.path.exists(MAIL_HANDLED_DIR):
                os.makedirs(MAIL_HANDLED_DIR)
            shutil.move(self.email_path, os.path.join(MAIL_HANDLED_DIR, self.email_filename))

            archive(False, scam_email, bait_email, res_text, MessengerOptions.EMAIL, subject)

    def handle_email(self):
        text = self.email_obj["content"]
        subject = self.add_re_to_subject(str(self.email_obj["title"]))
        scam_email = self.email_obj["from"]

        if "bait_email" not in self.email_obj:
            self.handle_crawled_email(scam_email, text, subject)
        else:
            self.handle_reply_email(scam_email, subject)
