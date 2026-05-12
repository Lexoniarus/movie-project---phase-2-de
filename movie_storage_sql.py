"""SQL storage helpers for the Movies application."""

from __future__ import annotations

from sqlalchemy import create_engine, text


DB_URL = "sqlite:///movies.db"

engine = create_engine(DB_URL, echo=True)

with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL
        )
    """))
    connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating FROM movies")
        )
        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
        }
        for row in movies
    }


def add_movie(title, year, rating):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating)
                    VALUES (:title, :year, :rating)
                """),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
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
