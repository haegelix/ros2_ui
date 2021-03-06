# importing third party modules
import subprocess
import re
import threading

# importing ros2_ui modules
from typing import IO, AnyStr

from ros2_ui.exceptions.packageexception import PackageException
from ros2_ui.interfaces.Log import logging

"""
empty strings may contain tabs, spaces, newlines, carriage returns, underscores and hyphens.
Despite containing any number of those characters they still count as empty.
"""
pattern_empty_string = re.compile(r'[\n\t\r _-]*')


def runcommand(command: str, shortname: str, logger=logging):
    """
    Run a third party application.

    :param command: The command to be run. Contains all parameters too.
    :param shortname: The shortname to be used for logging the execution and corresponding outputs.
    :param logger: The logger to be used.
    :return: Nothing.
    :raises PackageException: Raised if the application returns a non-zero exit value.
    """
    shortname += "..."

    # Split command without splitting nested Strings.
    pattern = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
    cmd = pattern.split(command)

    # delete al empty strings
    cmd = [c for c in cmd if c and c != ' ']

    # unquote
    cmd = [c.replace("\"", "").replace("'", "") for c in cmd]
    # logger.debug(cmd)
    logger.info("Running '" + shortname + "'")

    # run the command and deal with output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return_val = proc.wait()
    stdout, stderr = proc.communicate()
    if not len(pattern_empty_string.sub("", str(stdout))) == 0:  # stdout not empty --> log it
        logger.info("STDOUT of '" + shortname + "':\n" + str(stdout))
    if not len(pattern_empty_string.sub("", str(stderr))) == 0:  # stderr not empty --> log it
        logger.info("STDERR of '" + shortname + "':\n" + str(stderr))
    logger.info(shortname + " returned code " + str(return_val))
    if return_val != 0:
        raise PackageException("Aborted because one step ('" + shortname + "') failed!")


loggers_enabled = True

def log_while_running(stream: IO[AnyStr], stream_name: str, logger=logging):
    """
    Log everything coming in via a specific stream to a logger of choice.

    :param stream: Stream in question.
    :param stream_name: Name of the stream.
    :param logger: Logger to be used.
    :return: Nothing.
    """
    for line in iter(stream.readline, b''):
        if not loggers_enabled:
            return
        if not len(pattern_empty_string.sub("", str(line))) == 0:
            logger.info('{0}: {1}'.format(stream_name, line[:-1]))


proc: subprocess.Popen


def stop_launch():
    proc.terminate()


def runcommand_continuous_output(command: str, shortname: str, logger=logging):
    """
    Run a third party application. Does not block while execution but outputs all output immediately.

    :param command: The command to be run. Contains all parameters too.
    :param shortname: The shortname to be used for logging the execution and corresponding outputs.
    :param logger: The logger to be used.
    :return: Nothing.
    :raises PackageException: Raised if the application returns a non-zero exit value.
    """
    global proc, loggers_enabled

    shortname += "..."

    # Split command without splitting nested Strings.
    pattern = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
    cmd = pattern.split(command)

    # delete al empty strings
    cmd = [c for c in cmd if c and c != ' ']

    # unquote
    cmd = [c.replace("\"", "").replace("'", "") for c in cmd]
    logger.info("Running '" + shortname + "'")

    # run the command and deal with output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # start logger threads
    loggers_enabled = True
    log_stdout = threading.Thread(target=log_while_running, args=(proc.stdout, "stdout", logger))
    log_stderr = threading.Thread(target=log_while_running, args=(proc.stderr, "stderr", logger))

    log_stdout.start()
    log_stderr.start()

    # await end of subprocess
    return_val = proc.wait()
    logger.info(shortname + " returned code " + str(return_val))
    loggers_enabled = False

    # await logger threads terminations
    log_stdout.join()
    log_stderr.join()
