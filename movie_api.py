"""Helpers for retrieving movie data from the OMDb API."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


OMDB_API_URL = "http://www.omdbapi.com/"
API_KEY_ENV_NAME = "OMDB_API_KEY"


def fetch_movie_data(title, api_key=None):
    """Fetch a single movie by title from the OMDb API."""
    api_key = api_key or os.getenv(API_KEY_ENV_NAME)

    if not api_key:
        print("Error: OMDB_API_KEY is not set.")
        return None

    query_string = urlencode(
        {
            "apikey": api_key,
            "t": title,
        }
    )
    request_url = f"{OMDB_API_URL}?{query_string}"

    try:
        with urlopen(request_url, timeout=10) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as error:
        print(f"HTTP error while fetching movie data: {error}")
        return None
    except URLError as error:
        print(f"Network error while fetching movie data: {error}")
        return None

    movie_data = json.loads(response_body)

    if movie_data.get("Response") == "False":
        print(f"Error: {movie_data.get('Error')}")
        return None

    return movie_data
