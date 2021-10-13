"""Neocities client."""

import requests

from .filetree import FileTree
from .log import debug


class BearerAuth(requests.auth.AuthBase):
    """Bearer token authentication functor for requests."""

    __token: str

    def __init__(self, token: str):
        """
        Initialize object.

        Parameters
        ----------
        token: str
            The bearer token.
        """
        self.__token = token

    def __call__(self, req: requests.Request):
        """Add auth token to request."""
        req.headers["Authorization"] = f"Bearer {self.__token}"
        return req


class Neocities:
    """Neocities client."""

    __auth: BearerAuth
    __base_url: str

    def __init__(self, api_key: str, base_url: str = "https://neocities.org/api"):
        """
        Initialize the client.

        Parameters
        ----------
        api_key : str
            The API key to use.
        base_url : str
            The base URL of the API.
        """
        self.__auth = BearerAuth(api_key)
        self.__base_url = base_url

    def list(self) -> FileTree:
        """
        List all files in the site.

        Returns
        -------
        FileTree
            A FileTree object containing all files in the site.
        """
        url = f"{self.__base_url}/list"
        debug("Listing files...")
        result = requests.get(url, auth=self.__auth)
        if result.status_code == 200:
            debug("Listed files.")
            return FileTree(result.json().get("files"))
        else:
            raise Exception(
                f'Server returned "{result.status_code} {result.reason}" when loading "{url}"'
            )

    def upload(self, file: str):
        """
        Upload a file to the site.

        Parameters
        ----------
        file : str
            The path to the file to upload.

        Returns
        -------
        None
        """
        url = f"{self.__base_url}/upload"
        debug(f"Uploading {file}...")
        result = requests.post(url, auth=self.__auth, files={file: open(file, "rb")})
        if result.status_code != 200:
            raise Exception(
                f'Server returned "{result.status_code} {result.reason}" when uploading "{file}"'
            )
        debug(f"Uploaded {file}.")

    def delete(self, file: str):
        """
        Delete a file from the site.

        Parameters
        ----------
        file : str
            The path to the file to delete.

        Returns
        -------
        None
        """
        url = f"{self.__base_url}/delete"
        debug(f"Deleting {file}...")
        result = requests.post(url, auth=self.__auth, data={"filenames[]": file})
        if result.status_code != 200:
            raise Exception(
                f'Server returned "{result.status_code} {result.reason}" when deleting "{file}"'
            )
        debug(f"Deleted {file}.")
