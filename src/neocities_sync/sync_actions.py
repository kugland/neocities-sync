"""Actions needed to sync local with remote file trees."""

from typing import Generator, List, Optional

from .filetree import FileTree, FileTreeEntry


class SyncAction:
    """Action to be done on the remote file tree."""

    path: str
    reason: str

    def __init__(self, path: str, reason: str):
        """
        Initialize a new instance of the SyncAction class.

        Parameters
        ----------
        path : str
            Path to the file or directory to be acted upon
        reason : str
            Reason for the action
        """
        self.path = path
        self.reason = reason

    def __repr__(self):  # noqa: D105
        path = self.path
        reason = self.reason
        return f"{self.__class__.__name__}({path=}, {reason=})"


class DoNothing(SyncAction):
    """Do nothing."""

    def __init__(self, path: str, reason: str):  # noqa: D107
        super().__init__(path, reason)


class DeleteRemote(SyncAction):
    """Delete a remote file/directory."""

    def __init__(self, path: str, reason: str):  # noqa: D107
        super().__init__(path, reason)


class UpdateRemote(SyncAction):
    """Update a remote file."""

    def __init__(self, path: str, reason: str):  # noqa: D107
        super().__init__(path, reason)


def _choose_action_for_pair(local: Optional[FileTreeEntry], remote: Optional[FileTreeEntry]) -> List[SyncAction]:
    """
    Generate actions to update local and remote file tree entries.

    Parameters
    ----------
    local : FileTreeEntry
        The local file tree entry.
    remote : FileTreeEntry
        The remote file tree entry.

    Returns
    -------
    Action
        The action to update remote file tree.

    >>> foobar_entry = FileTreeEntry(
    ...     path='/foo/bar',
    ...     is_directory=False,
    ...     updated_at="Sat, 13 Feb 2016 03:04:00 -0000",
    ...     size=123,
    ...     sha1_hash="41fe08fc0dd44e79f799d03ece903e62be25dc7d"
    ... )
    ...
    >>> foobar_entry_changed_size = FileTreeEntry(
    ...     path='/foo/bar',
    ...     is_directory=False,
    ...     updated_at="Sat, 13 Feb 2016 03:04:00 -0000",
    ...     size=456,
    ...     sha1_hash="41fe08fc0dd44e79f799d03ece903e62be25dc7d"
    ... )
    ...
    >>> foobar_entry_changed_hash = FileTreeEntry(
    ...     path='/foo/bar',
    ...     is_directory=False,
    ...     updated_at="Sat, 13 Feb 2016 03:04:00 -0000",
    ...     size=123,
    ...     sha1_hash="e293275f23a11972fde3032f93784de8c16ed384"
    ... )
    ...
    >>> foobar_entry_directory = FileTreeEntry(
    ...     path='/foo/bar',
    ...     is_directory=True,
    ...     updated_at="Sat, 13 Feb 2016 03:04:00 -0000",
    ... )
    ...
    >>> _choose_action_for_pair(None, None)
    []
    >>> _choose_action_for_pair(None, foobar_entry)
    [DeleteRemote(path='/foo/bar', reason="File doesn't exist locally")]
    >>> _choose_action_for_pair(foobar_entry, None)
    [UpdateRemote(path='/foo/bar', reason="File doesn't exist in remote")]
    >>> _choose_action_for_pair(foobar_entry, foobar_entry)
    [DoNothing(path='/foo/bar', reason='No action needed')]
    >>> _choose_action_for_pair(foobar_entry, foobar_entry_changed_size)
    [UpdateRemote(path='/foo/bar', reason='Sizes differ')]
    >>> _choose_action_for_pair(foobar_entry, foobar_entry_changed_hash)
    [UpdateRemote(path='/foo/bar', reason="SHA1 hashes don't match")]
    >>> _choose_action_for_pair(foobar_entry, foobar_entry_directory)  # doctest: +NORMALIZE_WHITESPACE
    [DeleteRemote(path='/foo/bar', reason='Path is a directory in remote'),
     UpdateRemote(path='/foo/bar', reason='Path is a directory in remote')]
    >>> _choose_action_for_pair(foobar_entry_directory, foobar_entry)
    [DeleteRemote(path='/foo/bar', reason='Path is a directory locally')]
    """
    if local is None and remote is None:
        return []  # This should never happen, but just in case.
    elif local is None:
        return [DeleteRemote(remote.path, "File doesn't exist locally")]
    elif remote is None:
        return [UpdateRemote(local.path, "File doesn't exist in remote")]
    elif local.is_directory and remote.is_directory:
        return []  # This should never happen, but just in case.
    elif (not local.is_directory) and (remote.is_directory):
        return [
            DeleteRemote(local.path, "Path is a directory in remote"),
            UpdateRemote(local.path, "Path is a directory in remote"),
        ]
    elif (local.is_directory) and (not remote.is_directory):
        return [DeleteRemote(remote.path, "Path is a directory locally")]
    elif local.size != remote.size:
        return [UpdateRemote(local.path, "Sizes differ")]
    elif local.sha1_hash != remote.sha1_hash:
        return [UpdateRemote(local.path, "SHA1 hashes don't match")]
    return [DoNothing(local.path, "No action needed")]


def sync_actions(local: FileTree, remote: FileTree) -> Generator[SyncAction, None, None]:
    """
    Generate actions to update local and remote file tree entries.

    Parameters
    ----------
    local : FileTree
        The local file tree.
    remote : FileTree
        The remote file tree.

    Yields
    ------
    Action
        The action to update remote file tree.

    >>> local = FileTree([{
    ...     "path": "index.html",
    ...     "is_directory": False,
    ...     "size": 1023,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
    ... }, {
    ...     "path": "not_found_in_remote.html",
    ...     "is_directory": False,
    ...     "size": 271,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "cfdf0bda2557c322be78302da23c32fec72ffc0b"
    ... }, {
    ...     "path": "images",
    ...     "is_directory": False,
    ...     "size": 271,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "cfdf0bda2557c322be78302da23c32fec72ffc0b"
    ... }, {
    ...     "path": "dir_locally",
    ...     "is_directory": True,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ... }, {
    ...     "path": "different_sizes",
    ...     "is_directory": False,
    ...     "size": 271,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "cfdf0bda2557c322be78302da23c32fec72ffc0b"
    ... }, {
    ...     "path": "different_hashes",
    ...     "is_directory": False,
    ...     "size": 333,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "63793f46c4d966f710974a0219e05641b0e49e42"
    ... }])
    ...
    >>> remote = FileTree([{
    ...     "path": "index.html",
    ...     "is_directory": False,
    ...     "size": 1023,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
    ... }, {
    ...     "path": "not_found_in_local.html",
    ...     "is_directory": False,
    ...     "size": 271,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "cfdf0bda2557c322be78302da23c32fec72ffc0b"
    ... }, {
    ...     "path": "images",
    ...     "is_directory": True,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
    ... }, {
    ...     "path": "images/cat.png",
    ...     "is_directory": False,
    ...     "size": 16793,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "41fe08fc0dd44e79f799d03ece903e62be25dc7d"
    ... }, {
    ...     "path": "dir_locally",
    ...     "is_directory": False,
    ...     "size": 16793,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "41fe08fc0dd44e79f799d03ece903e62be25dc7d"
    ... }, {
    ...     "path": "different_sizes",
    ...     "is_directory": False,
    ...     "size": 333,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "cfdf0bda2557c322be78302da23c32fec72ffc0b"
    ... }, {
    ...     "path": "different_hashes",
    ...     "is_directory": False,
    ...     "size": 333,
    ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
    ...     "sha1_hash": "33d1be055986a1abb1b31b6506abdf321d9b696b"
    ... }])
    ...
    >>> for action in sync_actions(local, remote):
    ...     print(action)
    ...
    UpdateRemote(path='different_hashes', reason="SHA1 hashes don't match")
    UpdateRemote(path='different_sizes', reason='Sizes differ')
    DeleteRemote(path='dir_locally', reason='Path is a directory locally')
    DeleteRemote(path='images', reason='Path is a directory in remote')
    UpdateRemote(path='images', reason='Path is a directory in remote')
    DoNothing(path='index.html', reason='No action needed')
    DeleteRemote(path='not_found_in_local.html', reason="File doesn't exist locally")
    UpdateRemote(path='not_found_in_remote.html', reason="File doesn't exist in remote")
    """
    deleted: List[str] = []  # Keeps track of deleted files/directories
    for local_entry, remote_entry in local.zip(remote):
        for current_action in _choose_action_for_pair(local_entry, remote_entry):
            if isinstance(current_action, DeleteRemote):
                if len([p for p in deleted if current_action.path.startswith(p + "/")]) > 0:
                    # If the path is a subdirectory of a deleted directory, don't need to delete it
                    continue
                else:
                    deleted.append(current_action.path)
            yield current_action


if __name__ == "__main__":
    import doctest

    doctest.testmod()
