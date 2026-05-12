"""SQL storage helpers for the Movies application."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_FILE_PATH = DATA_DIR / "movies.db"
DB_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}"

DATA_DIR.mkdir(exist_ok=True)
engine = create_engine(DB_URL, echo=True)


def _create_users_table():
    """Create the users table if it does not exist."""
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """))
        connection.commit()


def _create_movies_table():
    """Create the movies table if it does not exist."""
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                poster_url TEXT,
                note TEXT,
                imdb_id TEXT,
                country TEXT,
                country_flag TEXT,
                UNIQUE(user_id, title),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """))
        connection.commit()


def _recreate_movies_table():
    """Recreate the movies table for the current user-profile schema."""
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS movies"))
        connection.commit()

    _create_movies_table()


def _ensure_movies_schema():
    """Ensure the movies table contains user profile columns."""
    with engine.connect() as connection:
        result = connection.execute(text("PRAGMA table_info(movies)"))
        column_names = [row[1] for row in result.fetchall()]

    if "user_id" not in column_names:
        _recreate_movies_table()
        return

    missing_columns = {
        "note": "ALTER TABLE movies ADD COLUMN note TEXT",
        "imdb_id": "ALTER TABLE movies ADD COLUMN imdb_id TEXT",
        "country": "ALTER TABLE movies ADD COLUMN country TEXT",
        "country_flag": "ALTER TABLE movies ADD COLUMN country_flag TEXT",
    }

    for column_name, query in missing_columns.items():
        if column_name not in column_names:
            _add_movies_column(query)


def _add_movies_column(query):
    """Add a column to the movies table."""
    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()


_create_users_table()
_create_movies_table()
_ensure_movies_schema()


def list_users():
    """Retrieve all user profiles from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, name FROM users ORDER BY name")
        )
        users = result.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
        }
        for row in users
    ]


def add_user(name):
    """Add a new user profile and return its id."""
    with engine.connect() as connection:
        result = connection.execute(
            text("INSERT INTO users (name) VALUES (:name)"),
            {"name": name},
        )
        connection.commit()

    return result.lastrowid


def list_movies(user_id):
    """Retrieve all movies for one user from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    title,
                    year,
                    rating,
                    poster_url,
                    note,
                    imdb_id,
                    country,
                    country_flag
                FROM movies
                WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        )
        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3],
            "note": row[4],
            "imdb_id": row[5],
            "country": row[6],
            "country_flag": row[7],
        }
        for row in movies
    }


def add_movie(
    user_id,
    title,
    year,
    rating,
    poster_url="",
    imdb_id="",
    country="",
    country_flag="",
):
    """Add a new movie to one user's collection."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (
                        user_id,
                        title,
                        year,
                        rating,
                        poster_url,
                        imdb_id,
                        country,
                        country_flag
                    )
                    VALUES (
                        :user_id,
                        :title,
                        :year,
                        :rating,
                        :poster_url,
                        :imdb_id,
                        :country,
                        :country_flag
                    )
                """),
                {
                    "user_id": user_id,
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                    "imdb_id": imdb_id,
                    "country": country,
                    "country_flag": country_flag,
                },
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as error:
            print(f"Error: {error}")


def delete_movie(user_id, title):
    """Delete a movie from one user's collection."""
    with engine.connect() as connection:
        connection.execute(
            text("""
                DELETE FROM movies
                WHERE user_id = :user_id AND title = :title
            """),
            {
                "user_id": user_id,
                "title": title,
            },
        )
        connection.commit()

    print(f"Movie '{title}' deleted successfully.")


def update_movie(user_id, title, note):
    """Update a movie's note in one user's collection."""
    with engine.connect() as connection:
        connection.execute(
            text("""
                UPDATE movies
                SET note = :note
                WHERE user_id = :user_id AND title = :title
            """),
            {
                "user_id": user_id,
                "title": title,
                "note": note,
            },
        )
        connection.commit()

    print(f"Movie '{title}' updated successfully.")
