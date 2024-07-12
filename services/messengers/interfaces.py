from abc import ABC, abstractmethod


class MessengerInterface(ABC):

    @abstractmethod
    def send_message(self, *args, **kwargs):
        pass

    @abstractmethod
    def receive_message(self, data):
        pass
