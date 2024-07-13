import logging
from datetime import datetime
import requests

from constants import IO_TYPE, SCHEDULER_TYPE
from secret import API_BASE_URL, API_KEY, DOMAIN_NAME
from services.archiver import Archiver
from utils.logging_utils import initialise_logging_config
from utils.structures import MessengerOptions, Message, Conversation
from services.io_utils.factories import LoaderFactory, WriterFactory
from services.scheduler import SchedulerFactory
from services.messenger_switch_detector import MessengerSwitchDetector
from services.messengers.interfaces import MessengerInterface


class EmailMessenger(MessengerInterface):
    def __init__(self):
        self.loader = LoaderFactory.get_loader(IO_TYPE)
        self.writer = WriterFactory.get_writer(IO_TYPE)
        self.switch_detector = MessengerSwitchDetector()
        self.scheduler = SchedulerFactory.get_scheduler(SCHEDULER_TYPE)
        self.archiver = Archiver()
        self.template = self.loader.load_mail_template()

    def receive_message(self, data):
        cleaned_data = self.clean_data(data)
        message = self.create_message(cleaned_data)

        if self.loader.scam_exists(message.from_addr):
            conversation = self.loader.load_conversation(message.from_addr)
        else:
            conversation = self.create_new_conversation(message)

        self.process_message(message, conversation)

    @staticmethod
    def clean_data(data):
        cleaned_data = {key.strip("'"): value for key, value in data.items()}
        return cleaned_data

    def create_message(self, cleaned_data):
        from_addr = str(cleaned_data["sender"]).lower()
        to_addr = self.extract_recipient(cleaned_data["recipient"])
        subject = cleaned_data["Subject"]
        content = cleaned_data["stripped-text"]

        if "stripped-signature" in cleaned_data:
            content += "\n" + cleaned_data["stripped-signature"]

        return Message(
            is_inbound=True,
            from_addr=from_addr,
            to_addr=to_addr,
            time=datetime.timestamp(datetime.now()),
            medium=MessengerOptions.EMAIL,
            body=content,
            subject=subject
        )

    @staticmethod
    def extract_recipient(raw_recipient):
        if "," in raw_recipient:
            for rec in raw_recipient.split(","):
                if rec.endswith(DOMAIN_NAME):
                    return rec
        else:
            return raw_recipient

    def create_new_conversation(self, message):
        unique_scam_id = self.loader.get_unique_scam_id(message.from_addr)
        pause_start, pause_end = self.scheduler.get_pause_times()

        return Conversation(
            unique_scam_id=unique_scam_id,
            scam_ids={MessengerOptions.EMAIL: message.from_addr},
            bait_ids={MessengerOptions.EMAIL: message.to_addr},
            pause_start=pause_start,
            pause_end=pause_end,
            already_queued=False,
            victim_name=None
        )

    def process_message(self, message, conversation):
        conversation.add_message(message)

        next_response_time = self.scheduler.get_next_response_time(
            datetime.timestamp(datetime.now()),
            conversation.pause_start,
            conversation.pause_end
        )

        switch_predict = self.switch_detector.predict_switch(message.body)
        switch_medium = (
            switch_predict.messenger
            if switch_predict.messenger != MessengerOptions.OTHER
            else MessengerOptions.EMAIL
        )
        if conversation.already_queued:
            initialise_logging_config()
            logging.getLogger().trace(f"Conversation {conversation.unique_id} is already queued, skipping")
        else:
            self.writer.schedule_response(
                message.from_addr,
                next_response_time.timestamp(),
                message.medium,
                switch_medium
            )
            conversation.already_queued = True
        self.archiver.archive_conversation(conversation)

    def send_message(self, message: Message, username: str):
        if isinstance(message.to_addr, str):
            target = [message.to_addr]
        else:
            target = message.to_addr

        initialise_logging_config()
        logging.getLogger().trace(f"Trying to send an email from {message.from_addr} to {message.to_addr}")

        html_content = self.template.replace("{{{content}}}", message.body).replace("\n", "<br>")

        res = requests.post(
            f"https://api.mailgun.net/v3/{API_BASE_URL}/messages",
            auth=("api", API_KEY),
            data={
                "from": f"{username} <{message.from_addr}>",
                "to": target,
                "subject": message.subject,
                "html": html_content
            }
        )

        if "Queued." not in res.text:
            logging.getLogger().trace(f"Failed to send, {res.text}")
            return False

        return True
