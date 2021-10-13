"""Assorted utility functions."""

import hashlib
import os
from typing import Callable

from .log import debug


def file_extension(file: str) -> str:
    """
    Return the file extension of the given file.

    Parameters
    ----------
    file : str
        The file to get the extension of.

    Returns
    -------
    str
        The file extension.

    >>> file_extension('/path/to/file.ext')
    '.ext'
    >>> file_extension('/path/to/file')
    ''
    >>> file_extension('/path/to/file.abc.def')
    '.def'
    >>> file_extension('/path/to/.bashrc')
    ''
    """
    return os.path.splitext(file)[1]


def path_match_any_element(path: str, condition: Callable[[str], bool]) -> bool:
    """
    Return True if any element of the path matches a given condition.

    Parameters
    ----------
    path : str
        The path to check.
    condition : Callable[[str], bool]
        A function that takes a string and returns True if the string matches.

    Returns
    -------
    bool
        True if any element of the path matches the condition.

    >>> path_match_any_element("/foo/bar/baz", lambda x: x.startswith("b"))
    True
    >>> path_match_any_element("/foo/bar/baz", lambda x: x.startswith("a"))
    False
    >>> path_match_any_element("/foo/.git/baz", lambda x: x in [".git", ".hg", ".svn", ".bzr"])
    True
    >>> path_match_any_element("/foo/bar/.git", lambda x: x in [".git", ".hg", ".svn", ".bzr"])
    True
    """
    return any(condition(elem) for elem in path.split("/"))


class Pushd:
    """Enter a directory and return to the previous directory when done."""

    def __init__(self, new_path):  # noqa: D107
        """
        Enter a directory and return to the previous directory when done.

        Parameters
        ----------
        new_path : str
            The directory to enter.
        """
        self.new_path = new_path
        self.old_path = os.getcwd()

    def __enter__(self):  # noqa: D105
        debug(f'Entering directory "{self.new_path}".')
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):  # noqa: D105
        debug(f'Leaving "{self.new_path}".')
        os.chdir(self.old_path)


def sha1file(file: str) -> str:
    """
    Calculate the SHA1 hash of a file.

    Parameters
    ----------
    file : str
        The path to the file

    Returns
    -------
    str
        The SHA1 hash of the file
    """
    with open(file, "rb") as f:
        hash = hashlib.sha1()
        while True:
            data = f.read(1024)
            if not data:
                break
            hash.update(data)
        return hash.hexdigest()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
