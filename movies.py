"""Command line interface for the Movies application."""

from __future__ import annotations

import statistics
from datetime import datetime

import movie_storage


MIN_RATING = 0.0
MAX_RATING = 10.0
MIN_YEAR = 1888
MAX_YEAR = datetime.now().year + 10
VALID_MENU_CHOICES = {str(number) for number in range(10)}


def print_menu():
    """Print the application menu."""
    print("Menu:")
    print("0. Exit")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Stats")
    print("6. Search movie")
    print("7. Sort movies by rating")
    print("8. Sort movies by year")
    print("9. Filter movies")


def prompt_menu_choice():
    """Prompt the user for a valid menu choice."""
    while True:
        choice = input("Enter choice (0-9): ").strip()

        if choice in VALID_MENU_CHOICES:
            return choice

        print("Invalid choice. Please enter a number from 0 to 9.")


def prompt_non_empty_title(prompt_text):
    """Prompt the user for a non empty movie title."""
    while True:
        title = input(prompt_text).strip()

        if title:
            return title

        print("Movie title cannot be empty.")


def prompt_rating(prompt_text, allow_blank=False):
    """Prompt the user for a valid movie rating."""
    while True:
        user_input = input(prompt_text).strip()

        if allow_blank and user_input == "":
            return None

        try:
            rating = float(user_input)
        except ValueError:
            print("Invalid rating. Please enter a number.")
            continue

        if rating < MIN_RATING or rating > MAX_RATING:
            print("Invalid rating. Please enter a value from 0 to 10.")
            continue

        return rating


def prompt_year(prompt_text, allow_blank=False):
    """Prompt the user for a valid release year."""
    while True:
        user_input = input(prompt_text).strip()

        if allow_blank and user_input == "":
            return None

        try:
            year = int(user_input)
        except ValueError:
            print("Invalid year. Please enter a whole number.")
            continue

        if year < MIN_YEAR or year > MAX_YEAR:
            print(
                f"Invalid year. Please enter a value from {MIN_YEAR} "
                f"to {MAX_YEAR}."
            )
            continue

        return year


def prompt_yes_no(prompt_text):
    """Prompt the user for a yes or no answer."""
    while True:
        answer = input(prompt_text).strip().lower()

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Invalid choice. Please enter y or n.")


def display_movie_entries(movie_entries):
    """Display a list of movie entries."""
    for title, details in movie_entries:
        print(f"{title} ({details['year']}): {details['rating']:.1f}")


def list_movies():
    """Display all movies with their release year and rating."""
    movies = movie_storage.get_movies()

    if not movies:
        print("No movies found.")
        return

    print(f"{len(movies)} movies in total")
    display_movie_entries(sorted(movies.items(), key=lambda item: item[0].lower()))


def add_movie():
    """Add a new movie to the storage."""
    movies = movie_storage.get_movies()
    title = prompt_non_empty_title("Enter new movie name: ")

    if title in movies:
        print(f"Movie '{title}' already exists!")
        return

    year = prompt_year("Enter movie year: ")
    rating = prompt_rating("Enter movie rating: ")

    movie_storage.add_movie(title, year, rating)
    print(f"Movie '{title}' successfully added.")


def delete_movie():
    """Delete a movie from the storage."""
    movies = movie_storage.get_movies()
    title = prompt_non_empty_title("Enter movie name to delete: ")

    if title not in movies:
        print(f"Movie '{title}' doesn't exist!")
        return

    movie_storage.delete_movie(title)
    print(f"Movie '{title}' successfully deleted.")


def update_movie():
    """Update the rating of an existing movie."""
    movies = movie_storage.get_movies()
    title = prompt_non_empty_title("Enter movie name to update: ")

    if title not in movies:
        print(f"Movie '{title}' doesn't exist!")
        return

    rating = prompt_rating("Enter new movie rating: ")
    movie_storage.update_movie(title, rating)
    print(f"Movie '{title}' successfully updated.")


def show_stats():
    """Display rating statistics for all movies."""
    movies = movie_storage.get_movies()

    if not movies:
        print("No movies found.")
        return

    ratings = [details["rating"] for details in movies.values()]
    best_movie = max(movies.items(), key=lambda item: item[1]["rating"])
    worst_movie = min(movies.items(), key=lambda item: item[1]["rating"])

    print(f"Movies count: {len(movies)}")
    print(f"Average rating: {statistics.mean(ratings):.1f}")
    print(f"Median rating: {statistics.median(ratings):.1f}")
    print(f"Best movie: {best_movie[0]}, {best_movie[1]['rating']:.1f}")
    print(f"Worst movie: {worst_movie[0]}, {worst_movie[1]['rating']:.1f}")


def search_movie():
    """Search movies by a partial title match."""
    movies = movie_storage.get_movies()

    if not movies:
        print("No movies found.")
        return

    search_term = prompt_non_empty_title("Enter part of movie name: ").lower()
    matching_movies = [
        (title, details)
        for title, details in movies.items()
        if search_term in title.lower()
    ]

    if not matching_movies:
        print("No movies found.")
        return

    print("Search results:")
    display_movie_entries(
        sorted(matching_movies, key=lambda item: item[0].lower())
    )


def sort_movies_by_rating():
    """Display movies sorted by rating."""
    movies = movie_storage.get_movies()

    if not movies:
        print("No movies found.")
        return

    highest_first = prompt_yes_no("Show highest rated movies first? (y/n): ")
    sorted_movies = sorted(movies.items(), key=lambda item: item[0].lower())
    sorted_movies = sorted(
        sorted_movies,
        key=lambda item: item[1]["rating"],
        reverse=highest_first,
    )

    print("Movies sorted by rating:")
    display_movie_entries(sorted_movies)


def sort_movies_by_year():
    """Display movies sorted by release year."""
    movies = movie_storage.get_movies()

    if not movies:
        print("No movies found.")
        return

    newest_first = prompt_yes_no("Show newest movies first? (y/n): ")
    sorted_movies = sorted(movies.items(), key=lambda item: item[0].lower())
    sorted_movies = sorted(
        sorted_movies,
        key=lambda item: item[1]["year"],
        reverse=newest_first,
    )

    print("Movies sorted by year:")
    display_movie_entries(sorted_movies)


def filter_movies():
    """Display movies filtered by rating and release year."""
    movies = movie_storage.get_movies()

    if not movies:
        print("No movies found.")
        return

    minimum_rating = prompt_rating(
        "Enter minimum rating (leave blank for no minimum rating): ",
        allow_blank=True,
    )
    start_year = prompt_year(
        "Enter start year (leave blank for no start year): ",
        allow_blank=True,
    )
    end_year = prompt_year(
        "Enter end year (leave blank for no end year): ",
        allow_blank=True,
    )

    if (
        start_year is not None
        and end_year is not None
        and start_year > end_year
    ):
        print("Invalid range. Start year cannot be greater than end year.")
        return

    filtered_movies = []

    for title, details in movies.items():
        if minimum_rating is not None and details["rating"] < minimum_rating:
            continue

        if start_year is not None and details["year"] < start_year:
            continue

        if end_year is not None and details["year"] > end_year:
            continue

        filtered_movies.append((title, details))

    if not filtered_movies:
        print("No movies found.")
        return

    print("Filtered movies:")
    display_movie_entries(
        sorted(filtered_movies, key=lambda item: item[0].lower())
    )


def handle_menu_choice(choice):
    """Execute the action that belongs to the chosen menu option."""
    if choice == "1":
        list_movies()
    elif choice == "2":
        add_movie()
    elif choice == "3":
        delete_movie()
    elif choice == "4":
        update_movie()
    elif choice == "5":
        show_stats()
    elif choice == "6":
        search_movie()
    elif choice == "7":
        sort_movies_by_rating()
    elif choice == "8":
        sort_movies_by_year()
    elif choice == "9":
        filter_movies()


def main():
    """Run the Movies application."""
    while True:
        print_menu()
        choice = prompt_menu_choice()

        if choice == "0":
            print("Bye!")
            break

        handle_menu_choice(choice)
        print()


if __name__ == "__main__":
    main()
