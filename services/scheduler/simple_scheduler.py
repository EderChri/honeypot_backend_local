from services.scheduler import SchedulerInterface
import random
from datetime import datetime, timedelta


class SimpleScheduler(SchedulerInterface):
    def __init__(self, pause_interval, min_response_wait, max_response_wait):
        self.pause_interval = pause_interval
        self.min_response_wait = min_response_wait * 60  # Convert to minutes
        self.max_response_wait = max_response_wait * 60  # Convert to minutes

    def get_pause_times(self):
        pause_start = random.randint(0, 23)
        pause_end = (pause_start + self.pause_interval) % 24
        return pause_start, pause_end

    def get_next_response_time(self, timestamp, pause_start, pause_end):
        dt = datetime.fromtimestamp(timestamp)

        minutes_to_add = random.randint(self.min_response_wait, self.max_response_wait)
        pause_start_dt = dt.replace(hour=pause_start, minute=0, second=0, microsecond=0)
        pause_end_dt = dt.replace(hour=pause_end, minute=0, second=0, microsecond=0)

        # Check if the pause period crosses midnight
        if pause_start >= pause_end:
            pause_end_dt += timedelta(days=1)

        if pause_start_dt <= dt <= pause_end_dt:
            next_response_time = pause_end_dt + timedelta(minutes=minutes_to_add)
        else:
            next_response_time = dt + timedelta(minutes=minutes_to_add)
            if pause_start_dt <= next_response_time <= pause_end_dt:
                next_response_time = pause_end_dt + timedelta(minutes=minutes_to_add)

        return next_response_time
