import logging as logg
from logging.handlers import QueueHandler
from queue import SimpleQueue
from logging import handlers

from ros2_ui.settings import settings


class LogAdapter(logg.LoggerAdapter):
    """
    LogAdapter handles log messages to be able to alter them before they are being presented.
    """
    def process(self, msg, kwargs):
        """
        Alter messages adding indents.

        :param msg: Message to be processed.
        :param kwargs: More parameters.
        :return: Altered messages and kwargs.
        """
        ms = str(msg)
        ms = ms.replace("\n", "\n|    ")
        return ms, kwargs


def setup_logging(filename: str):
    """
    Set up logging.

    :param filename: Filename of the file the log should be flowing towards.
    :return:
    """
    # set loglevel
    root_logger = logg.getLogger()
    root_logger.setLevel(logg.DEBUG)

    # output log to logfile
    log_fmt_file = logg.Formatter('%(asctime)s %(levelname)s - %(message)s', '%m.%d.%Y %H:%M:%S')
    file_handler = logg.FileHandler(filename)
    file_handler.setFormatter(log_fmt_file)
    root_logger.addHandler(file_handler)

    # output log to stdout
    log_fmt_stdout = logg.Formatter('%(message)s')
    console_handler = logg.StreamHandler()
    console_handler.setFormatter(log_fmt_stdout)
    root_logger.addHandler(console_handler)

    # set levelnames to be 4 chars long
    logg.addLevelName(logg.NOTSET, 'NTST')
    logg.addLevelName(logg.DEBUG, 'DBUG')
    logg.addLevelName(logg.INFO, 'INFO')
    logg.addLevelName(logg.WARNING, 'WARN')
    logg.addLevelName(logg.ERROR, 'ERRR')
    logg.addLevelName(logg.CRITICAL, 'CRIT')


# to be run on import
logging = LogAdapter(logg.getLogger(), None)
setup_logging(settings.log_path)


def get_queue_logger(q: SimpleQueue, logger_name="") -> logg.Logger:
    """
    Build a new queue-logger. You can logg to it like to a standard logger.

    :param q: Queue to be used for logging.
    :param logger_name: Name for the new logger.
    :return: A fresh logger.
    """
    # get new logger
    logger = logg.getLogger(logger_name)

    # set format
    log_fmt_stdout = logg.Formatter('%(asctime)s %(levelname)s - %(message)s', '%H:%M:%S')

    # create Queue handler & return
    queue_handler = QueueHandler(q)
    queue_handler.setFormatter(log_fmt_stdout)
    logger.addHandler(queue_handler)
    return logger
