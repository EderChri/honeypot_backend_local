from .interfaces import MessengerInterface
from .emailmessenger import EmailMessenger
from utils.structures import MessengerOptions


class MessengerFactory:
    @staticmethod
    def get_messenger(service_type: MessengerOptions) -> MessengerInterface:
        match service_type:
            case MessengerOptions.EMAIL:
                return EmailMessenger()
            case _:
                raise ValueError(f"Unknown service type: {service_type}")
