from services.scheduler import SimpleScheduler
from constants import PAUSE_TIME, MIN_RESPONSE_WAIT, MAX_RESPONSE_WAIT


class SchedulerFactory:
    @staticmethod
    def get_scheduler(scheduler_type):
        if scheduler_type == "Simple":
            return SimpleScheduler(PAUSE_TIME, MIN_RESPONSE_WAIT, MAX_RESPONSE_WAIT)
        else:
            raise ValueError("Unsupported scheduler type")
