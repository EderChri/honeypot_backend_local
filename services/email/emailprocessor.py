import os
import json
import shutil
import traceback

from constants import IO_TYPE
from services.io_utils.factories import WriterFactory, LoaderFactory
from services import solution_manager, responder, mailgun
from services.archiver import Archiver
from utils.structures import MessengerOptions


class EmailProcessor:
    def __init__(self, email_filename):
        self.email_filename = email_filename
        self.writer = WriterFactory.get_writer(IO_TYPE)
        self.loader = LoaderFactory.get_loader(IO_TYPE)
        self.email_obj = self.loader.load_scam_data(email_filename)

    @staticmethod
    def add_re_to_subject(subject):
        if not subject.startswith("Re:"):
            subject = "Re: " + subject
        return subject

    def handle_crawled_email(self, scam_email, text, subject):
        if solution_manager.scam_exists(scam_email):
            print("This crawled email has been replied, ignoring")
            self.writer.remove_scam_from_queue(scam_email)
            return

        print("This email is just crawled, using random replier")
        replier = responder.get_replier_by_name("MailReplier")
        bait_email = solution_manager.gen_new_addr(scam_email, replier.name)
        stored_info = solution_manager.get_stored_info(bait_email, scam_email)

        archiver = Archiver()
        archiver.archive(True, scam_email, "CRAWLER", text, MessengerOptions.EMAIL, self.email_obj["title"])

        self.generate_and_send_reply(stored_info, scam_email, replier, subject, bait_email)

    def handle_reply_email(self, scam_email, subject):
        bait_email = self.email_obj["bait_email"]
        stored_info = solution_manager.get_stored_info(bait_email, scam_email)

        if stored_info is None:
            print(f"Cannot find replier for {bait_email}")
            self.writer.remove_scam_from_queue(scam_email)
            return

        print(f"Found selected replier {stored_info.sol}")
        replier = responder.get_replier_by_name(stored_info.sol)

        if replier is None:
            print("Replier Sol_name not found")
            self.writer.remove_scam_from_queue(scam_email)
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
            self.writer.move_from_queued_to_handled(scam_email)
            archiver = Archiver()
            archiver.archive(False, scam_email, bait_email, res_text, MessengerOptions.EMAIL, subject)

    def handle_email(self):
        text = self.email_obj["content"]
        subject = self.add_re_to_subject(str(self.email_obj["title"]))
        scam_email = self.email_obj["from"]

        if "bait_email" not in self.email_obj:
            self.handle_crawled_email(scam_email, text, subject)
        else:
            self.handle_reply_email(scam_email, subject)
