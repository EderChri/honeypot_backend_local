from datetime import datetime


class Scammer:
    def __init__(self, scam_id, start_hour, end_hour):
        self.scam_id = scam_id
        self.start_hour = start_hour
        self.end_hour = end_hour

    def should_respond(self):
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour < self.end_hour
