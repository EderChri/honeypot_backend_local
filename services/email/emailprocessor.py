import logging
import time
import traceback

import names

from constants import IO_TYPE, SCHEDULER_TYPE, CRAWLER_FLAG
from services.io_utils.factories import WriterFactory, LoaderFactory
from services.scheduler import SchedulerFactory
from services import responder
from services.messengers import MessengerFactory
from services.archiver import Archiver
from utils.logging_utils import log
from utils.structures import MessengerOptions, Message, Conversation
from utils.common import get_random_addr


class EmailProcessor:
    def __init__(self, unique_scam_id, queued_response):
        self.writer = WriterFactory.get_writer(IO_TYPE)
        self.loader = LoaderFactory.get_loader(IO_TYPE)
        self.archiver = Archiver()
        self.queued_response = queued_response
        self.scheduler = SchedulerFactory.get_scheduler(SCHEDULER_TYPE)
        self.conversation = self.loader.load_conversation(unique_scam_id, is_unique_id=True)
        self.email_messenger = MessengerFactory.get_messenger(MessengerOptions.EMAIL)

    @staticmethod
    def add_re_to_subject(subject):
        if not subject.startswith("Re:"):
            subject = "Re: " + subject
        return subject

    def handle_crawled_email(self):
        scam_email = self.conversation.scam_ids[MessengerOptions.EMAIL]
        text = self.conversation.messages[0].body
        subject = self.conversation.messages[0].subject
        if self.loader.scam_exists(scam_email):
            print("This crawled email has been replied, ignoring")
            self.writer.remove_scam_from_queue(scam_email)
            return

        print("This email is just crawled, using random replier")
        replier = responder.get_replier_by_name("MailReplier")
        bait_email = get_random_addr()

        message = Message(is_inbound=True, from_addr=scam_email, to_addr=CRAWLER_FLAG, time=int(time.time()),
                          medium=MessengerOptions.EMAIL, body=text, subject=subject)
        pause_start, pause_end = self.scheduler.get_pause_times()
        conversation = Conversation(
            unique_scam_id=self.loader.get_unique_scam_id(scam_email),
            scam_ids={MessengerOptions.EMAIL: scam_email}, victim_ids={MessengerOptions.EMAIL: bait_email},
            pause_start=pause_start, pause_end=pause_end,
            already_queued=False, victim_name=names.get_first_name())
        conversation.add_message(message)
        self.conversation = conversation
        self.archiver.archive_conversation(conversation)

        self.generate_and_send_reply(replier, subject)

    def handle_reply_email(self):
        subject = self.conversation.messages[0].subject

        replier = responder.get_replier_by_name(MessengerOptions.EMAIL)

        self.generate_and_send_reply(replier, subject)

    def add_signature(self, res_text):
        if self.conversation.victim_name is not None:
            res_text += f"\nBest,\n{self.conversation.victim_name}"
        else:
            self.conversation.victim_name = names.get_first_name()
            res_text += f"\nBest,\n{self.conversation.victim_name}"
            self.archiver.archive_conversation(self.conversation)
        return res_text

    def generate_and_send_reply(self, replier, subject):
        try:
            res_text = replier.get_reply_by_his(self.conversation.unique_id, is_unique_id=True)
        except Exception as e:
            log("GENERATING ERROR")
            log(e)
            log(traceback.format_exc())
            print("Due to CUDA Error, stopping whole sequence")
            return
        scam_email = self.conversation.scam_ids[MessengerOptions.EMAIL]
        bait_email = self.conversation.victim_ids[MessengerOptions.EMAIL]
        res_text = self.add_signature(res_text)

        message = Message(False, bait_email, scam_email, time.time(),
                          MessengerOptions.EMAIL, res_text, subject)

        send_result = self.email_messenger.send_message(message, self.conversation.victim_name)
        if send_result:
            log(f"Successfully sent response to {scam_email}")
            self.conversation.add_message(message)
            self.writer.move_from_queued_to_handled(self.conversation, self.queued_response)

    def handle_email(self):
        if CRAWLER_FLAG == self.conversation.messages[-1].to_addr:
            self.handle_crawled_email()
        else:
            self.handle_reply_email()
