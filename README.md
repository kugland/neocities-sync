# neocities-sync
**Sync local directories with neocities.org sites.**

## Usage:

`neocities-sync [options] [--dry-run] [-c CONFIG] [-s SITE1] [-s SITE2] ...`


### Options:

- `-C CONFIG_FILE`:

    Path to the config file to use. (defaults to `~/.config/neocities-sync.conf`.)

- `-s SITE`:

    Which site to sync (as specified in the config file). The default is to sync all sites in the config file.

- `--dry-run`:

    Do not actually upload anything.

- `-v`:

    Verbose output.

- `-q`:

    Quiet output.

- `-h, --help`:

    Show help message and exit.

## Config file

The config file is an ini file, located at `~/.config/neocities-sync.conf`.

Each section of the config file describes a different site (the name of the
section doesn't need to be the same as the site's domain, since the `api_key`
suffices to identify the site).

The keys of the config file are:

- `api_key`: the api key of the site. **(required)**

- `root_dir`: the local directory to sync. **(required)**

- `sync_disallowed`: whether to sync file types that are only allowed for paying users. **(default: no)**

- `sync_hidden` is whether to sync hidden files. **(default: no)**

- `sync_vcs`: whether to sync version control files. **(default: no)**

- `allowed_extensions`: which file extensions to sync. (If not set, all files are synced.) **(default: not set)**

- `remove_empty_dirs`: whether to remove empty directories after sync. **(default: yes)**

### Example config:

```ini
[site1]
api_key = 6b9b522e7d8d93e88c464aafc421a61b
root_dir = ~/path/to/site1
allowed_extensions = .html .css .js
remove_empty_dirs = no

[site2]
api_key = 78559e6ebc35fe33eec21de05666a243
root_dir = /var/www/path/to/site2
allowed_extensions = .html .css .js .woff2
```


## .neocitiesignore

In any subdirectory of the root directory, a file named `.neocitiesignore`    can be used to specify which files to ignore.  The syntax is the same as the one for git’s `.gitignore`.


## Credits:

This software was developed by Andre Kugland &lt;kugland@gmail.com&gt;.
