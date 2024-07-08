from abc import ABC, abstractmethod


class Loader(ABC):
    @abstractmethod
    def load_schedule(self, timestamp):
        pass

    @abstractmethod
    def load_history(self, id):
        pass

    @abstractmethod
    def get_scam_ids(self):
        pass

    @abstractmethod
    def get_unique_scam_id(self, scam_id):
        pass
