"""Beautiful logging."""

import sys
from datetime import datetime
from enum import Enum

from .colors import blue, bri_black, bri_blue, bri_green, bri_red, bri_yellow, cyan, green, red, yellow  # noqa I001
# noqa I005


class LogLevel(Enum):
    """Log levels."""

    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4
    NONE = 5

    def __str__(self):  # noqa: D105
        if self == LogLevel.DEBUG:
            return blue("[") + bri_blue("debug") + blue("]")
        elif self == LogLevel.INFO:
            return green("[") + bri_green("info") + green("]") + " "
        elif self == LogLevel.WARN:
            return yellow("[") + bri_yellow("warn") + yellow("]") + " "
        elif self == LogLevel.ERROR:
            return red("[") + bri_red("error") + red("]")
        elif self == LogLevel.FATAL:
            return red("[") + bri_red("fatal") + red("]")

    def stream(self):
        """Return the stream to write to."""
        switcher = {
            LogLevel.DEBUG: sys.stdout,
            LogLevel.INFO: sys.stdout,
            LogLevel.WARN: sys.stderr,
            LogLevel.ERROR: sys.stderr,
            LogLevel.FATAL: sys.stderr,
        }
        return switcher.get(self, sys.stdout)


_min_level = LogLevel.INFO.value


def increase_verbosity():
    """Increase log verbosity."""
    global _min_level
    if _min_level > LogLevel.DEBUG.value:
        _min_level -= 1


def decrease_verbosity():
    """Decrease log verbosity."""
    global _min_level
    if _min_level < LogLevel.NONE.value:
        _min_level += 1


def _log(level: LogLevel, message: str):
    """Log messages."""
    if _min_level <= level.value:
        datetime_prefix = cyan(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        level_prefix = str(level)
        stream = level.stream()
        log_message = f"{datetime_prefix} {bri_black('|')} {level_prefix}  "
        for lineno, line in enumerate(message.splitlines()):
            if lineno > 0:
                log_message += " " * 31
            log_message += line
            log_message += "\n"
        stream.write(log_message)
        stream.flush()


def debug(message: str):
    """Print a debug message."""
    _log(LogLevel.DEBUG, message)


def info(message: str):
    """Print an info message."""
    _log(LogLevel.INFO, message)


def warn(message: str):
    """Print a warning message."""
    _log(LogLevel.WARN, message)


def error(message: str):
    """Print an error message."""
    _log(LogLevel.ERROR, message)


def fatal(message: str):
    """Print a fatal message."""
    _log(LogLevel.FATAL, message)
