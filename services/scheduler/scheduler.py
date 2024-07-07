import schedule
import time
import random
from datetime import datetime
from scammer import Scammer


class Scheduler:
    def __init__(self, scammers):
        self.scammers = scammers

    def respond_scammer(self, scammer):
        print(f"Answering scam {scammer.scam_id} at {datetime.now()}")

    def scheduled_task(self, scammer):
        if scammer.should_respond():
            delay = random.uniform(5, 30) * 60  # Random delay between 5 and 30 minutes
            time.sleep(delay)
            self.respond_scammer(scammer)
        else:
            print(f"Scammer {scammer.user_id} is not in the responding time frame at {datetime.now()}")

    def start(self):
        for scammer in self.scammers:
            schedule.every(10).seconds.do(self.scheduled_task, user=scammer)

        while True:
            schedule.run_pending()
            time.sleep(5 * 60)  # Check every 5 minutes
