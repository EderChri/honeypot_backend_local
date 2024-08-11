import logging
from constants import LOG_PATH, TRACE


def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)


def initialise_logging_config():
    logging.addLevelName(TRACE, "TRACE")
    logging.basicConfig(filename=LOG_PATH, level=TRACE, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.Logger.trace = trace


def log(message):
    initialise_logging_config()
    logging.getLogger().trace(message)