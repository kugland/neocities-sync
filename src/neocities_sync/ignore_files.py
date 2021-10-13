"""Ignore files according to config."""

import os

from .config import SiteConfig
from .filetree import FileTree
from .log import debug
from .treepathspec import TreePathSpec
from .utils import path_match_any_element

allowed_extensions = """
    asc atom bin css csv dae eot epub geojson gif gltf htm html ico jpeg jpg js json key kml
    knowl less manifest markdown md mf mid midi mtl obj opml otf pdf pgp png rdf rss sass scss
    svg text tsv ttf txt webapp webmanifest webp woff woff2 xcf xml
"""

vcs_files = set(".git .hg .svn .bzr ".split())


class IgnoreFiles:
    """Remove ignored files from the FileTree."""

    __config: SiteConfig
    __pathspec: TreePathSpec

    def __init__(self, config: SiteConfig):
        """
        Initialize the IgnoreFiles object.

        Parameters
        ----------
        config : SiteConfig
            The configuration for the site.
        """
        self.__config = config
        self.__pathspec = TreePathSpec(".", ".neocitiesignore")
        self.__pathspec.load()

    def filter(self, tree: FileTree) -> FileTree:
        """
        Remove ignored files from the FileTree.

        Parameters
        ----------
        tree : FileTree
            The FileTree to filter.

        Returns
        -------
        FileTree
            The filtered FileTree.
        """
        # Remove .neocitiesignore files.
        debug('Ignoring ".neocitiesignore" files...')
        tree = tree.filter(lambda f: os.path.basename(f.path) != ".neocitiesignore")

        if not self.__config.sync_disallowed:
            # Remove all files which don't have an allowed extension.
            exts = self.__config.allowed_extensions
            if exts is None:
                exts = allowed_extensions.split()
            exts = set([f'.{ext.lstrip(".").upper()}' for ext in exts])
            debug("Ignoring files with disallowed extensions...")
            tree = tree.filter(lambda f: f.is_directory or (f.extension.upper() in exts))

        # Remove ignored files.
        debug("Ignoring files matched by .neocitiesignore files...")
        tree = tree.filter(lambda f: not self.__pathspec.match(f.path))

        if not self.__config.sync_hidden:
            # Remove hidden files.
            debug("Ignoring hidden files...")
            tree = tree.filter(lambda f: not path_match_any_element(f.path, lambda p: p.startswith(".")))

        if not self.__config.sync_vcs:
            # Remove VCS files.
            debug("Ignoring version control files...")
            tree = tree.filter(lambda f: not path_match_any_element(f.path, lambda p: p in vcs_files))

        return tree
