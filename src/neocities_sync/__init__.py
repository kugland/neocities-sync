"""Sync local directories with neocities.org sites."""

import os
import sys

from . import cmdline
from . import local
from .config import load_config_file
from .ignore_files import IgnoreFiles
from .log import (debug, decrease_verbosity, error, fatal, increase_verbosity, info)
from .neocities import Neocities
from .sync_actions import DeleteRemote, DoNothing, UpdateRemote, sync_actions
from .utils import Pushd


def main():
    """Program entry-point."""
    cmdline_opts = cmdline.parse(sys.argv[1:])

    if cmdline_opts.quietness > 0:
        for _ in range(cmdline_opts.quietness):
            decrease_verbosity()
    elif cmdline_opts.quietness < 0:
        for _ in range(-cmdline_opts.quietness):
            increase_verbosity()

    try:
        conf = load_config_file(cmdline_opts.config_file)
    except FileNotFoundError:
        fatal(f'Config file "{cmdline_opts.config_file}" not found. Run again with "--help" for more info.')
        exit(1)

    for site, site_conf in conf.items():
        client = Neocities(site_conf.api_key)
        with Pushd(os.path.expanduser(site_conf.root_dir)):
            info(f'Starting sync for site "{site}".')
            info("Listing local file tree...")
            local_filetree = local.filetree(".")
            local_filetree = IgnoreFiles(site_conf).filter(local_filetree)
            info(
                f"Local file tree has {local_filetree.number_of_files()} file(s)"
                f" and {local_filetree.number_of_directories()} dir(s)."
            )
            info("Fetching remote file tree...")
            remote_filetree = client.list()
            info(
                f"Remote file tree has {remote_filetree.number_of_files()}"
                f" file(s) and {remote_filetree.number_of_directories()} dir(s)."
            )
            info("Comparing file trees...")
            applied_actions = 0
            for action in sync_actions(local_filetree, remote_filetree):
                try:
                    if isinstance(action, UpdateRemote):
                        info(f'Updating remote file "{action.path}": {action.reason}.')
                        if not cmdline_opts.dry_run:
                            client.upload(action.path)
                        applied_actions += 1
                    elif isinstance(action, DeleteRemote):
                        info(f'Deleting remote file "{action.path}": {action.reason}.')
                        if not cmdline_opts.dry_run:
                            client.delete(action.path)
                        applied_actions += 1
                    elif isinstance(action, DoNothing):
                        debug(f'Skipping "{action.path}": {action.reason}.')
                    else:
                        raise RuntimeError(f"Unknown action {action.__class__.__name__}.")
                except Exception as e:  # noqa: B902
                    error(f"Error while syncing: {e}")
                    exit(1)
            if not cmdline_opts.dry_run:
                info(f"Applied {applied_actions} action(s).")
            else:
                info(f"Would apply {applied_actions} action(s).")
            if site_conf.remove_empty_dirs:
                info("Searching for empty directories...")
                remote_filetree = client.list()
                empty_directories = remote_filetree.list_empty_directories()
                info(f"Found {len(empty_directories)} empty dir(s).")
                for empty_dir in sorted(empty_directories, reverse=True):
                    info(f'Deleting remote empty directory "{empty_dir}"')
                    if not cmdline_opts.dry_run:
                        client.delete(empty_dir)
            info(f'Finished sync for site "{site}".')

if __name__ == "__main__":
    main()
