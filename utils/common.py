from datetime import datetime

from services.io_utils.factories import LoaderFactory
from constants import IO_TYPE
from secret import DOMAIN_NAME
import random
import string


def get_random_addr():
    loader = LoaderFactory.get_loader(IO_TYPE)
    while True:
        res = ""
        for i in range(2):
            res += random.choice(string.ascii_lowercase)

        for i in range(5):
            res += random.choice(string.digits)

        if not loader.check_if_address_exists(res):
            return res + "@" + DOMAIN_NAME


def is_timestamp_in_past(timestamp_or_name):
    if isinstance(timestamp_or_name, str):
        timestamp = float(timestamp_or_name.rsplit('.', 2)[0])
    else:
        timestamp = timestamp_or_name
    return timestamp < datetime.timestamp(datetime.now())
