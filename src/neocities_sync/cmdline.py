"""Parse command line arguments."""

from argparse import ArgumentParser
from dataclasses import dataclass
from typing import List

from .config import config_file_path, config_file_path_unexpanded


@dataclass
class CmdlineOptions:
    """Command line options."""

    sites: List[str] = None
    quietness: int = 0
    dry_run: bool = False
    config_file: str = None
    help: bool = False


def parse(args: List[str]) -> CmdlineOptions:
    """
    Parse command line arguments.

    Parameters
    ----------
    args : List[str]
        List of command line arguments.

    Returns
    -------
    CmdlineOptions
        Command line options.

    >>> parse(['-C', 'myconf', '-qqq', '--dry-run', '--site=foo.com', '--site=bar.com'])
    CmdlineOptions(sites=['foo.com', 'bar.com'], quietness=3, dry_run=True, config_file='myconf', help=False)
    >>> parse(['-C', 'myconf', '-v', '--site=foo.com', '--site=bar.com'])
    CmdlineOptions(sites=['foo.com', 'bar.com'], quietness=-1, dry_run=False, config_file='myconf', help=False)
    >>> parse(['-C', 'myconf', '-vvqds', 'site'])
    CmdlineOptions(sites=['site'], quietness=-1, dry_run=True, config_file='myconf', help=False)
    """
    argparser = ArgumentParser(
        description="Sync local directories with a neocities.org remote.",
        add_help=False,
    )
    argparser.add_argument(
        "-s",
        "--site",
        help="which site to sync (can be used multiple times)",
        action="append",
        default=[],
    )
    argparser.add_argument('-C', '--config-file', default=config_file_path)
    argparser.add_argument("-d", "--dry-run", action="store_true")
    argparser.add_argument("-v", "--verbose", action="count", default=0)
    argparser.add_argument("-q", "--quiet", action="count", default=0)
    argparser.add_argument('-h', '--help', action='store_true', default=False)
    parsed = argparser.parse_args(args)

    if parsed.help:
        print(help_message())
        exit(0)

    return CmdlineOptions(
        sites=parsed.site,
        quietness=parsed.quiet - parsed.verbose,
        dry_run=parsed.dry_run,
        config_file=parsed.config_file,
        help=parsed.help,
    )


def help_message() -> str:
    """
    Return help message.

    Returns
    -------
    str
        Help message.
    """
    msg = f"""neocities-sync
Sync local directories with neocities.org sites.

Usage:

    neocities-sync options] [--dry-run] [-c CONFIG] [-s SITE1] [-s SITE2] ...


  Options:
      -C CONFIG_FILE      Path to the config file to use.
                          (defaults to "{config_file_path_unexpanded}".)
      -s SITE             Which site to sync (as specified in the config file).
                          The default is to sync all sites in the config file.
      --dry-run           Do not actually upload anything.

      -v                  Verbose output.
      -q                  Quiet output.
      -h, --help          Show this help message and exit.


Config file:

    The config file is an ini file, located at "{config_file_path_unexpanded}".

    Each section of the config file describes a different site (the name of the
    section doesn't need to be the same as the site's domain, since the api_key
    suffices to identify the site).

    The keys of the config file are:

        api_key (str)                                                [required]
            The api key of the site.

        root_dir (path)                                              [required]
            The local directory to sync.

        sync_disallowed (yes/no)                                  [default: no]
            Whether to sync files that are only allowed for paying users.

        sync_hidden (yes/no)                                      [default: no]
            Whether to sync hidden files.

        sync_vcs (yes/no)                                         [default: no]
            Whether to sync version control files.

        allowed_extensions (list of str)                     [default: not set]
            Which file extensions to sync.  If not set, all files are synced.

        remove_empty_dirs (yes/no)                               [default: yes]
            Whether to remove empty directories after sync.

  Example config:

        [site1]
        api_key = 6b9b522e7d8d93e88c464aafc421a61b
        root_dir = ~/path/to/site1
        allowed_extensions = .html .css .js
        remove_empty_dirs = no

        [site2]
        api_key = 78559e6ebc35fe33eec21de05666a243
        root_dir = /var/www/path/to/site2
        allowed_extensions = .html .css .js .woff2


.neocitiesignore

    In any subdirectory of the root directory, a file named ".neocitiesignore"
    can be used to specify which files to ignore.  The syntax is the same as
    the one for ".gitignore".


Credits:

    This software was developed by Andre Kugland <kugland@gmail.com>."""
    return msg


if __name__ == "__main__":
    import doctest

    doctest.testmod()
