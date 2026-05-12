"""Storage helpers for the Movies application."""

from __future__ import annotations

import json
from pathlib import Path


MOVIES_FILE_NAME = "movies.json"


def _get_file_path() -> Path:
    """Return the path to the JSON file that stores the movies."""
    return Path(__file__).resolve().parent / MOVIES_FILE_NAME


def get_movies():
    """Return all movies stored in the JSON file as a dictionary."""
    file_path = _get_file_path()

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            movies = json.load(handle)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

    if not isinstance(movies, dict):
        return {}

    return movies


def save_movies(movies):
    """Save the given movies dictionary to the JSON file."""
    file_path = _get_file_path()

    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(movies, handle, indent=4)


def add_movie(title, year, rating):
    """Add a movie to the JSON file and save the updated data."""
    movies = get_movies()
    movies[title] = {
        "rating": rating,
        "year": year,
    }
    save_movies(movies)


def delete_movie(title):
    """Delete a movie from the JSON file and save the updated data."""
    movies = get_movies()

    if title in movies:
        del movies[title]
        save_movies(movies)


def update_movie(title, rating):
    """Update a movie rating in the JSON file and save the data."""
    movies = get_movies()

    if title in movies:
        movies[title]["rating"] = rating
        save_movies(movies)
