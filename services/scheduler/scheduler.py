from abc import ABC, abstractmethod


class Scheduler(ABC):
    @abstractmethod
    def get_pause_times(self, timestamp):
        pass

    @abstractmethod
    def get_next_response_time(self, timestamp, pause_start, pause_end):
        pass
