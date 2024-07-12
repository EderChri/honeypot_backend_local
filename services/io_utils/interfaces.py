from abc import ABC, abstractmethod

from utils.structures import Conversation


class LoaderInterface(ABC):

    @abstractmethod
    def load_schedule_queue(self):
        pass

    @abstractmethod
    def load_scheduled_response(self, filename):
        pass

    @abstractmethod
    def load_conversation(self, scam_id):
        pass

    @abstractmethod
    def load_history(self, scam_id):
        pass

    @abstractmethod
    def get_scam_ids(self):
        pass

    @abstractmethod
    def get_unique_scam_id(self, scam_id, is_unique_id=False) -> str:
        pass

    @abstractmethod
    def scam_exists(self, scam_id) -> bool:
        pass

    @abstractmethod
    def load_mail_template(self):
        pass

    @abstractmethod
    def check_if_address_exists(self, address):
        pass


class WriterInterface(ABC):
    @abstractmethod
    def write_conversation(self, conversation: Conversation):
        pass

    @abstractmethod
    def write_history(self, conversation: Conversation):
        pass

    @abstractmethod
    def add_message(self, unique_scam_id, message):
        pass

    @abstractmethod
    def add_scam_id(self, unique_scam_id, scam_id):
        pass

    @abstractmethod
    def move_from_queued_to_handled(self, conversation, queued_response):
        pass

    @abstractmethod
    def remove_scam_from_queue(self, scam_id):
        pass

    @abstractmethod
    def add_scam_to_queue(self, scam_id, next_response_time, medium, switch_medium):
        pass
