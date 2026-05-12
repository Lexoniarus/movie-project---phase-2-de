"""SQL storage helpers for the Movies application."""

from __future__ import annotations

from sqlalchemy import create_engine, text


DB_URL = "sqlite:///movies.db"

engine = create_engine(DB_URL, echo=True)


def _create_movies_table():
    """Create the movies table if it does not exist."""
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                poster_url TEXT
            )
        """))
        connection.commit()


def _ensure_poster_url_column():
    """Add the poster_url column to older local databases."""
    with engine.connect() as connection:
        result = connection.execute(text("PRAGMA table_info(movies)"))
        column_names = [row[1] for row in result.fetchall()]

        if "poster_url" not in column_names:
            connection.execute(
                text("ALTER TABLE movies ADD COLUMN poster_url TEXT")
            )
            connection.commit()


_create_movies_table()
_ensure_poster_url_column()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster_url FROM movies")
        )
        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3],
        }
        for row in movies
    }


def add_movie(title, year, rating, poster_url=""):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster_url)
                    VALUES (:title, :year, :rating, :poster_url)
                """),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                },
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as error:
            print(f"Error: {error}")


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        connection.execute(
            text("DELETE FROM movies WHERE title = :title"),
            {"title": title},
        )
        connection.commit()

    print(f"Movie '{title}' deleted successfully.")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        connection.execute(
            text("UPDATE movies SET rating = :rating WHERE title = :title"),
            {
                "title": title,
                "rating": rating,
            },
        )
        connection.commit()

    print(f"Movie '{title}' updated successfully.")
