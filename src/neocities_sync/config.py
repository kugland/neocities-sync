"""Loading and parsing of the config file."""

import configparser
import os
from copy import copy
from dataclasses import dataclass
from typing import List, Optional

from .log import debug


@dataclass
class SiteConfig:
    """Configuration for a site."""

    root_dir: Optional[str] = None
    """Root directory of the site"""
    api_key: Optional[str] = None
    """API key for Neocities"""
    sync_disallowed: Optional[bool] = None
    """Whether to sync disallowed files"""
    sync_hidden: Optional[bool] = None
    """Whether to sync hidden files"""
    sync_vcs: Optional[bool] = None
    """Whether to sync version control files"""
    allowed_extensions: Optional[List[str]] = None
    """List of allowed extensions"""
    remove_empty_dirs: Optional[bool] = None

    def __str__(self):  # noqa: D105
        mapping = dict((key, value) for key, value in self.__dict__.items())
        mapping["api_key"] = "<redacted>"
        return "\n".join(f"{key}: {value}" for key, value in mapping.items())


def _merge_configs(first: SiteConfig, second: SiteConfig) -> SiteConfig:
    """Merge two configs together.

    Parameters
    ----------
    other : Config
        The config to merge with

    Returns
    -------
    Config
        The merged config

    >>> c1 = SiteConfig(root_dir='/home/user/site', api_key='12345')
    >>> c2 = SiteConfig(api_key='cc8f5d8a7df491aca644d6144d204bc6')
    >>> _merge_configs(c1, c2)  # doctest: +NORMALIZE_WHITESPACE
    SiteConfig(root_dir='/home/user/site',
               api_key='cc8f5d8a7df491aca644d6144d204bc6',
               sync_disallowed=None,
               sync_hidden=None,
               sync_vcs=None,
               allowed_extensions=None,
               remove_empty_dirs=None)
    """
    merged = copy(first)
    for attr in first.__dataclass_fields__:  # type: ignore
        if getattr(second, attr) is not None:
            setattr(merged, attr, getattr(second, attr))
    return merged


_default_config = SiteConfig(
    sync_disallowed=False,
    sync_hidden=False,
    sync_vcs=False,
    allowed_extensions=None,
    remove_empty_dirs=True,
)
"""Default configuration"""


def load_config(config_contents: str) -> dict[str, SiteConfig]:
    '''Parse a config file.

    Parameters
    ----------
    config_contents : str
        The contents of the config file

    Returns
    -------
    dict[str, Config]
        The parsed config (keyed by site name)

    >>> c = load_config("""[my_site]
    ... root_dir = /home/user/site
    ... api_key = cc8f5d8a7df491aca644d6144d204bc6
    ... sync_disallowed = yes
    ... allowed_extensions = .html .css .js
    ...
    ... [other_site]
    ... root_dir = /home/user/other_site
    ... api_key = d3aca528ab7256415d6f2b79dd3a7f9f
    ... sync_vcs = yes
    ... remove_empty_dirs = no
    ... """)
    >>> c['my_site']  # doctest: +NORMALIZE_WHITESPACE
    SiteConfig(root_dir='/home/user/site',
               api_key='cc8f5d8a7df491aca644d6144d204bc6',
               sync_disallowed=True,
               sync_hidden=False,
               sync_vcs=False,
               allowed_extensions=['.html', '.css', '.js'],
               remove_empty_dirs=True)
    >>> c['other_site']  # doctest: +NORMALIZE_WHITESPACE
    SiteConfig(root_dir='/home/user/other_site',
               api_key='d3aca528ab7256415d6f2b79dd3a7f9f',
               sync_disallowed=False,
               sync_hidden=False,
               sync_vcs=True,
               allowed_extensions=None,
               remove_empty_dirs=False)
    '''
    config = configparser.ConfigParser()
    config.read_string(config_contents)
    sites: dict[str, SiteConfig] = {}
    for site in config.sections():
        config_dict = {}
        for field in SiteConfig.__dataclass_fields__:  # type: ignore
            type_hint = SiteConfig.__annotations__[field]
            if type_hint is Optional[bool]:
                value = config.getboolean(site, field, fallback=None)
            elif type_hint is Optional[List[str]]:
                value = config.get(site, field, fallback=None)  # type: ignore
                if value is not None:
                    value = [v for v in value.split()]  # type: ignore
            else:
                value = config.get(site, field, fallback=None)  # type: ignore
            if value is not None:
                config_dict[field] = value
        sites[site] = _merge_configs(_default_config, SiteConfig(**config_dict))  # type: ignore
    return sites


config_file_path_unexpanded = "~/.config/neocities-sync.conf"
config_file_path = os.path.expanduser(config_file_path_unexpanded)


def load_config_file(config_file: str) -> dict[str, SiteConfig]:
    """
    Load the config file.

    Parameters
    ----------
    config_file : str
        The path to the config file

    Returns
    -------
    dict[str, Config]
        The parsed config (keyed by site name)
    """
    debug(f"Loading config file from {config_file}")
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found at {config_file}")
    with open(config_file, "r") as f:
        conf = load_config(f.read())
        for site in conf.keys():
            debug(f'Loaded config for site "{site}"\n{str(conf[site])}')
        return conf


if __name__ == "__main__":
    import doctest

    doctest.testmod()
