import pytest
from services.scheduler.factories import SchedulerFactory
from datetime import datetime
from constants import SCHEDULER_TYPE, PAUSE_TIME


@pytest.fixture
def simple_scheduler():
    return SchedulerFactory.get_scheduler(SCHEDULER_TYPE)


def test_get_pause_times(simple_scheduler):
    pause_start, pause_end = simple_scheduler.get_pause_times()
    assert 0 <= pause_start < 24
    assert 0 <= pause_end < 24
    assert abs((pause_end - pause_start) % 24) == PAUSE_TIME


def test_get_next_response_time_during_pause(simple_scheduler):
    timestamp = "2024-07-11 18:30:00"
    pause_start, pause_end = 18, 2

    next_response_time = simple_scheduler.get_next_response_time(timestamp, pause_start, pause_end)
    next_response_dt = datetime.strptime(next_response_time, "%Y-%m-%d %H:%M:%S")
    expected_pause_end = datetime.strptime("2024-07-12 02:00:00", "%Y-%m-%d %H:%M:%S")
    assert next_response_dt > expected_pause_end


def test_get_next_response_time_outside_pause(simple_scheduler):
    timestamp = "2024-07-11 03:30:00"
    pause_start, pause_end = 9, 17  # Example pause interval

    next_response_time = simple_scheduler.get_next_response_time(timestamp, pause_start, pause_end)
    next_response_dt = datetime.strptime(next_response_time, "%Y-%m-%d %H:%M:%S")
    timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    assert next_response_dt > timestamp_dt
