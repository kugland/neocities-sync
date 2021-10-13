"""Loads the local file tree."""

import email.utils
import os
from typing import Generator, List

from .filetree import FileTree, FileTreeEntry
from .utils import sha1file


def _list_files(path: str) -> Generator[str, None, None]:
    """
    List all files in the local directory.

    Parameters
    ----------
    path: str
        Path to the local directory.

    Yields
    ------
    str
        Files in the local directory.
    """
    if not os.path.isdir(path):
        raise RuntimeError(f"Not a directory: {path}")
    for filename in os.listdir(path):
        yield filename
        if os.path.isdir(os.path.join(path, filename)):
            for child in _list_files(os.path.join(path, filename)):
                yield os.path.join(filename, child)


def filetree(path: str) -> FileTree:
    """
    Get a file tree for the local directory.

    Parameters
    ----------
    path: str
        Path to the local directory.

    Returns
    -------
    FileTree
        File tree for the local directory.
    """
    tree_contents: List[FileTreeEntry] = []
    for filename in _list_files(path):
        filepath = os.path.join(path, filename)
        updated_at = email.utils.formatdate(os.path.getmtime(filepath))
        if os.path.isfile(filepath):
            entry = FileTreeEntry(
                path=filename,
                is_directory=False,
                size=os.path.getsize(filepath),
                updated_at=updated_at,
                sha1_hash=sha1file(filepath),
            )
            tree_contents.append(entry)
        elif os.path.isdir(filepath):
            entry = FileTreeEntry(path=filename, is_directory=True, updated_at=updated_at)
            tree_contents.append(entry)
        else:
            raise RuntimeError(f"{filepath} is neither a file nor a directory")
    return FileTree(tree_contents)
