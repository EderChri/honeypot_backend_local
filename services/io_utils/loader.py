from abc import ABC, abstractmethod


class Loader(ABC):
    @abstractmethod
    def load_schedule(self, timestamp):
        pass

    @abstractmethod
    def load_history(self, id):
        pass
