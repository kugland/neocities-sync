"""Color functions for logging."""

try:
    from colorama import Fore, Style, init

    init()

except ImportError:

    # no colorama, so just don't use colors.
    class Fore:
        """Dummy class to replace colorama.Fore."""

        BLACK = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""

    class Style:
        """Dummy class to replace colorama.Style."""

        RESET_ALL = ""
        BRIGHT = ""


def _color(color: str, bright: bool, text: str):
    if bright:
        return Style.BRIGHT + color + text + Style.RESET_ALL
    else:
        return color + text + Style.RESET_ALL


def black(text: str):
    """Make text black."""
    return _color(Fore.BLACK, False, text)


def bri_black(text: str):
    """Make text bright black."""
    return _color(Fore.BLACK, True, text)


def red(text: str):
    """Make text red."""
    return _color(Fore.RED, False, text)


def bri_red(text: str):
    """Make text bright red."""
    return _color(Fore.RED, True, text)


def green(text: str):
    """Make text green."""
    return _color(Fore.GREEN, False, text)


def bri_green(text: str):
    """Make text bright green."""
    return _color(Fore.GREEN, True, text)


def yellow(text: str):
    """Make text yellow."""
    return _color(Fore.YELLOW, False, text)


def bri_yellow(text: str):
    """Make text bright yellow."""
    return _color(Fore.YELLOW, True, text)


def blue(text: str):
    """Make text blue."""
    return _color(Fore.BLUE, False, text)


def bri_blue(text: str):
    """Make text bright blue."""
    return _color(Fore.BLUE, True, text)


def magenta(text: str):
    """Make text magenta."""
    return _color(Fore.MAGENTA, False, text)


def bri_magenta(text: str):
    """Make text bright magenta."""
    return _color(Fore.MAGENTA, True, text)


def cyan(text: str):
    """Make text cyan."""
    return _color(Fore.CYAN, False, text)


def bri_cyan(text: str):
    """Make text bright cyan."""
    return _color(Fore.CYAN, True, text)


def white(text: str):
    """Make text white."""
    return _color(Fore.WHITE, False, text)


def bri_white(text: str):
    """Make text bright white."""
    return _color(Fore.WHITE, True, text)
