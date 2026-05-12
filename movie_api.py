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


def get_movie_details(title, api_key=None):
    """Return normalized movie details for a single OMDb title."""
    movie_data = fetch_movie_data(title, api_key)

    if movie_data is None:
        return None

    rating = movie_data.get("imdbRating")

    if rating == "N/A":
        print("Error: Movie rating is not available.")
        return None

    try:
        year = int(movie_data["Year"][:4])
        rating = float(rating)
    except (KeyError, TypeError, ValueError):
        print("Error: Movie data is incomplete.")
        return None

    poster_url = movie_data.get("Poster", "")

    if poster_url == "N/A":
        poster_url = ""

    return {
        "title": movie_data["Title"],
        "year": year,
        "rating": rating,
        "poster_url": poster_url,
        "imdb_id": movie_data.get("imdbID", ""),
    }
