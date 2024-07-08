from abc import ABC, abstractmethod


class Writer(ABC):
    @abstractmethod
    def write_full_data(self, scam_id, content):
        pass

    @abstractmethod
    def write_history(self, scam_id, history, inbound_flag):
        pass

    @abstractmethod
    def add_scam_id(self, unique_scam_id, scam_id):
        pass
