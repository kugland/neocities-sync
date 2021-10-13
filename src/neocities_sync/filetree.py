"""Represents a local or a remote file tree."""

from dataclasses import dataclass
from typing import Callable, List, Optional, Union

from .log import debug
from .utils import file_extension


@dataclass(repr=False)
class FileTreeEntry:
    """Represents a file or a directory in a file tree."""

    path: str
    """Path of the file on the server"""
    is_directory: bool
    """True if the file is a directory"""
    updated_at: str
    """Last time the file was updated"""
    size: Optional[int] = None
    """Size of the file in bytes"""
    sha1_hash: Optional[str] = None
    """SHA1 hash of the file"""

    def __repr__(self) -> str:  # noqa: D105
        path, is_directory = self.path, self.is_directory
        if is_directory:
            return f"Directory({path=})"
        else:
            size, sha1_hash = self.size, self.sha1_hash
            return f"File({path=}, {size=}, {sha1_hash=})"

    @property
    def extension(self) -> str:
        """Extension of the file."""
        return file_extension(self.path)


class FileTree:
    """A local or a remote file tree."""

    __files: List[FileTreeEntry]

    def __init__(self, file_list: Union[List[dict], List[FileTreeEntry]]):
        """
        Create a file tree from a list of files.

        Parameters
        ----------
        file_list: Union[List[dict], List[FileTreeEntry]]
            List of containing information about files.

        >>> filetree = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }, {
        ...     "path": "not_found.html",
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
        ... }])
        ...
        >>> for file in filetree:
        ...     print(file.path)
        ...
        index.html
        not_found.html
        images
        images/cat.png
        """
        self.__files = []
        for file_data in file_list:
            if not isinstance(file_data, FileTreeEntry):
                file_data = FileTreeEntry(**file_data)
            self.__files.append(file_data)

    def __iter__(self):
        """Iterate over the files in the file tree."""
        return iter(self.__files)

    def number_of_files(self) -> int:
        """
        Get the number of files (i.e. excluding directories) in the file tree.

        Returns
        -------
        int
            Number of files in the file tree.

        >>> file_tree = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }, {
        ...     "path": "directory",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }])
        ...
        >>> file_tree.number_of_files()
        1
        """
        return len([file for file in self if not file.is_directory])

    def number_of_directories(self) -> int:
        """
        Get the number of directories in the file tree.

        Returns
        -------
        int
            Number of directories in the file tree.

        >>> file_tree = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }, {
        ...     "path": "directory",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }])
        ...
        >>> file_tree.number_of_directories()
        1
        """
        return len([file for file in self if file.is_directory])

    def find(self, path: str) -> Optional[FileTreeEntry]:
        """
        Find a file or directory by path.

        Parameters
        ----------
        path: str
            Path of the file or directory to find.

        Returns
        -------
        Optional[FileTreeEntry]
            File or directory found.

        >>> file_tree = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }])
        ...
        >>> file_tree.find("index.html")  # doctest: +NORMALIZE_WHITESPACE
        File(path='index.html',
             size=1023,
             sha1_hash='c8aac06f343c962a24a7eb111aad739ff48b7fb1')
        >>> file_tree.find("not_found.html") is None
        True
        """
        for file in self:
            if file.path == path:
                return file
        return None

    def filter(self, condition: Callable[[FileTreeEntry], bool]) -> "FileTree":
        """
        Filter the file tree by a condition.

        Parameters
        ----------
        condition: Callable[[FileTreeEntry], bool]
            Condition to filter by.

        Returns
        -------
        FileTree
            List of files that match the condition.

        >>> filetree = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }, {
        ...     "path": "not_found.html",
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
        ... }])
        ...
        >>> import log
        >>> log.decrease_verbosity()
        >>> for entry in filetree.filter(lambda file: file.path.endswith(".html")):  # doctest: +NORMALIZE_WHITESPACE
        ...     print(entry)
        ...
        File(path='index.html',
             size=1023,
             sha1_hash='c8aac06f343c962a24a7eb111aad739ff48b7fb1')
        File(path='not_found.html',
             size=271,
             sha1_hash='cfdf0bda2557c322be78302da23c32fec72ffc0b')
        """
        new_tree = FileTree([file for file in self if condition(file)])
        debug(f"Removed files: {[file.path for file in self if not condition(file)]}.")
        debug(f"New file tree has {self.number_of_files()} file(s) and {self.number_of_directories()} dir(s).")
        return new_tree

    def is_empty_dir(self, path: str) -> bool:
        """
        Check if a directory is empty.

        A directory is considered empty if it contains no files or only empty directories.

        Parameters
        ----------
        path: str
            Path of the directory to check.

        Returns
        -------
        bool
            True if the directory is empty, False otherwise.

        >>> filetree = FileTree([{
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
        ...     "path": "empty-directory",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }, {
        ...     "path": "empty-directory/empty-child",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }, {
        ...     "path": "really-empty",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }])
        ...
        >>> filetree.is_empty_directory("images")
        False
        >>> filetree.is_empty_directory("images/cat.png")
        False
        >>> filetree.is_empty_directory("empty-directory")
        True
        >>> filetree.is_empty_directory("empty-directory/empty-child")
        True
        >>> filetree.is_empty_directory("really-empty")
        True
        """
        # Test if path exists and is a directory
        directory = self.find(path)
        if directory is None or not directory.is_directory:
            return False
        # Find all files in the directory
        for file in self:
            # If there’s a file in the directory, then the directory isn’t empty.
            if file.path.startswith(path + "/") and not file.is_directory:
                return False
        return True

    def zip(self, other: "FileTree") -> List[tuple[Optional[FileTreeEntry], Optional[FileTreeEntry]]]:
        """
        Zip two file trees together.

        Parameters
        ----------
        other: FileTree
            Other file tree to zip with.

        Returns
        -------
        List[tuple[Optional[FileTreeEntry], Optional[FileTreeEntry]]]
            List of tuples containing files in self and other, respectively.
            If a file doesn't appear in one of the trees, it will be None.
            Directories are ignored.

        >>> ft1 = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }, {
        ...     "path": "only_in_this_tree.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
        ... }])
        ...
        >>> ft2 = FileTree([{
        ...     "path": "index.html",
        ...     "is_directory": False,
        ...     "size": 1023,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000",
        ...     "sha1_hash": "c8aac06f343c962a24a7eb111aad739ff48b7fb1"
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
        ... }])
        ...
        >>> for entry in ft1.zip(ft2):  # doctest: +NORMALIZE_WHITESPACE
        ...     print(entry)
        ...
        (None,
         File(path='images/cat.png',
              size=16793,
              sha1_hash='41fe08fc0dd44e79f799d03ece903e62be25dc7d'))
        (File(path='index.html',
              size=1023,
              sha1_hash='c8aac06f343c962a24a7eb111aad739ff48b7fb1'),
         File(path='index.html',
              size=1023,
              sha1_hash='c8aac06f343c962a24a7eb111aad739ff48b7fb1'))
        (File(path='only_in_this_tree.html',
              size=1023,
              sha1_hash='c8aac06f343c962a24a7eb111aad739ff48b7fb1'),
        None)
        """
        self_paths = [file.path for file in self if not file.is_directory]
        other_paths = [file.path for file in other if not file.is_directory]
        # Sorting is important (1) to ensure deterministic results for testing and (2) so that
        # a directory will always come before its children (which will be a prerequisite
        # for the generation of actions later on).
        all_paths = sorted(set(self_paths + other_paths))
        return [(self.find(path), other.find(path)) for path in all_paths]

    def list_empty_directories(self) -> List[str]:
        """
        Get all empty directories in the tree.

        Returns
        -------
        List[str]
            List of empty directories.

        >>> filetree = FileTree([{
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
        ...     "path": "empty-directory",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }, {
        ...     "path": "empty-directory/empty-child",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }, {
        ...     "path": "really-empty",
        ...     "is_directory": True,
        ...     "updated_at": "Sat, 13 Feb 2016 03:04:00 -0000"
        ... }])
        ...
        >>> filetree.list_empty_directories()
        ['empty-directory', 'empty-directory/empty-child', 'really-empty']
        """
        return [directory.path for directory in self if directory.is_directory and self.is_empty_dir(directory.path)]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
