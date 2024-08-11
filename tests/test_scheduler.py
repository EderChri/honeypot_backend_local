from datetime import datetime
from constants import PAUSE_TIME


def test_get_pause_times(simple_scheduler):
    pause_start, pause_end = simple_scheduler.get_pause_times()
    assert 0 <= pause_start < 24
    assert 0 <= pause_end < 24
    assert abs((pause_end - pause_start) % 24) == PAUSE_TIME


def test_get_next_response_time_during_pause(simple_scheduler):
    timestamp = datetime.strptime("2024-07-11 18:30:00", "%Y-%m-%d %H:%M:%S").timestamp()
    pause_start, pause_end = 18, 2

    next_response_time = simple_scheduler.get_next_response_time(timestamp, pause_start, pause_end)
    expected_pause_end = datetime.strptime("2024-07-12 02:00:00", "%Y-%m-%d %H:%M:%S")
    assert next_response_time > expected_pause_end


def test_get_next_response_time_outside_pause(simple_scheduler):
    timestamp = datetime.strptime("2024-07-11 03:30:00", "%Y-%m-%d %H:%M:%S").timestamp()
    pause_start, pause_end = 9, 17

    next_response_time = simple_scheduler.get_next_response_time(timestamp, pause_start, pause_end)
    assert next_response_time.timestamp() > timestamp
