"""Functionality similar to .gitignore etc for file trees."""

import os
from typing import List, Tuple

from pathspec import PathSpec

from .log import debug


def _add_slash(path: str) -> str:
    """
    Add a slash to the beginning of a path if it doesn't already have one and convert ./ to /.

    Parameters
    ----------
    path : str
        The path to add a slash to.

    Returns
    -------
    str
        The path with a slash added to the beginning.

    >>> _add_slash('/home/user/')
    '/home/user/'
    >>> _add_slash('home/user')
    '/home/user'
    >>> _add_slash('.')
    '/'
    >>> _add_slash('/')
    '/'
    >>> _add_slash('test')
    '/test'
    >>> _add_slash('./test')
    '/test'
    """
    if path == ".":
        return "/"
    if path.startswith("./"):
        return path[1:]
    if not path.startswith("/"):
        return "/" + path
    return path


class TreePathSpec:
    """Implements functionality similar to .gitignore etc for file trees."""

    __root_dir: str
    __pathspec_name: str
    __pathspec_list: List[Tuple[str, PathSpec]]

    def __init__(self, root_dir: str, pathspec_name: str):
        """
        Initialize a TreePathSpec object.

        Parameters
        ----------
        root_dir : str
            The root directory of the pathspec.
        pathspec_name : str
            The name of the pathspec file.
        """
        self.__root_dir = root_dir
        self.__pathspec_name = pathspec_name
        self.__pathspec_list = []

    def _load_pathspec(self, spec_root: str, lines: List[str]):
        """
        Load a pathspec from a list of lines.

        Parameters
        ----------
        spec_root : str
            The root directory of the pathspec.
        lines : List[str]
            The lines of the pathspec.

        Returns
        -------
        None

        >>> spec = TreePathSpec('.', '.testignore')
        >>> spec._load_pathspec('/txt', ['*.txt', '!allowed.txt'])
        >>> spec.match('/txt/test.txt')
        True
        >>> spec.match('/txt/allowed.txt')
        False
        """
        self.__pathspec_list.append((spec_root, PathSpec.from_lines("gitwildmatch", lines)))

    def match(self, file: str) -> bool:
        """
        Check if a file matches the pathspec.

        Parameters
        ----------
        file: str
            The relative path of the file

        Returns
        -------
        bool
            True if the file matches the pathspec, False otherwise

        >>> spec = TreePathSpec('.', '.testignore')
        >>> spec._load_pathspec('/txt', ['*.txt', '!allowed.txt'])
        >>> spec._load_pathspec('/py', ['*.py'])
        >>> spec._load_pathspec('/', ['*.pyc', '/py/*.abc', '!allowed.pyc'])
        >>> spec.match('/test.abc')
        False
        >>> spec.match('/test.py')
        False
        >>> spec.match('/test.pyc')
        True
        >>> spec.match('/test.txt')
        False
        >>> spec.match('/py/test.abc')
        True
        >>> spec.match('/txt/allowed.pyc')
        False
        >>> spec.match('/py/test.py')
        True
        >>> spec.match('/py/test.txt')
        False
        >>> spec.match('/py/test.pyc')
        True
        >>> spec.match('/txt/allowed.txt')
        False
        >>> spec.match('/txt/test.txt')
        True
        """
        for root, spec in self.__pathspec_list:
            relpath = os.path.relpath(file, root)
            if not relpath.startswith("../"):
                if spec.match_file(_add_slash(relpath)):
                    return True
        return False

    def load(self):
        """
        Recursively load pathspecs from a directory.

        Parameters
        ----------
        root_directory: str
            The directory to load pathspecs from

        Returns
        -------
        None
        """
        for root, dirs, files in os.walk(self.__root_dir):
            if self.__pathspec_name in files:
                debug(f'Loading pathspec "{os.path.join(root, self.__pathspec_name)}".')
                with open(os.path.join(root, self.__pathspec_name), "r") as f:
                    self._load_pathspec(_add_slash(root), f.readlines())
        # Reverse sort the pathspec list by the root directory, so that the
        # pathspec for a child directory is loaded before the pathspec for
        # its parent.
        self.__pathspec_list.sort(key=lambda x: x[0], reverse=True)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
