from abc import ABC, abstractmethod


class Writer(ABC):
    @abstractmethod
    def write_full_data(self, scam_id, content):
        pass

    @abstractmethod
    def write_history(self, scam_id, history, inbound_flag):
        pass
