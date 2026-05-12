"""Command line interface for the Movies application."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re
import statistics
from datetime import datetime

import movie_api
from storage import movie_storage_sql as storage


MIN_RATING = 0.0
MAX_RATING = 10.0
MIN_YEAR = 1888
MAX_YEAR = datetime.now().year + 10
STATIC_DIR = Path(__file__).resolve().parent / "_static"
TEMPLATE_FILE_PATH = STATIC_DIR / "index_template.html"
VALID_MENU_CHOICES = {str(number) for number in range(12)}


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
    print("9. Generate website")
    print("10. Filter movies")
    print("11. Switch user")


def prompt_menu_choice():
    """Prompt the user for a valid menu choice."""
    while True:
        choice = input("Enter choice (0-11): ").strip()

        if choice in VALID_MENU_CHOICES:
            return choice

        print("Invalid choice. Please enter a number from 0 to 11.")


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


def create_user():
    """Create a new user profile and return it."""
    while True:
        name = prompt_non_empty_title("Enter new user name: ")
        users = storage.list_users()

        if any(user["name"].lower() == name.lower() for user in users):
            print(f"User '{name}' already exists.")
            continue

        user_id = storage.add_user(name)
        print(f"User '{name}' created successfully.")

        return {
            "id": user_id,
            "name": name,
        }


def select_user():
    """Prompt the user to select or create a profile."""
    while True:
        users = storage.list_users()

        print("Welcome to the Movie App!")
        print("Select a user:")

        for index, user in enumerate(users, start=1):
            print(f"{index}. {user['name']}")

        create_choice = len(users) + 1
        print(f"{create_choice}. Create new user")

        choice = input("Enter choice: ").strip()

        try:
            selected_index = int(choice)
        except ValueError:
            print("Invalid choice. Please enter a number.")
            continue

        if selected_index == create_choice:
            return create_user()

        if 1 <= selected_index <= len(users):
            selected_user = users[selected_index - 1]
            print(f"Welcome back, {selected_user['name']}!")
            return selected_user

        print("Invalid choice. Please select one of the listed options.")


def list_movies(user):
    """Display all movies with their release year and rating."""
    movies = storage.list_movies(user["id"])

    if not movies:
        print(f"{user['name']}, your movie collection is empty.")
        return

    print(f"{len(movies)} movies in total")
    display_movie_entries(
        sorted(movies.items(), key=lambda item: item[0].lower())
    )


def add_movie(user):
    """Add a new movie to the storage."""
    movies = storage.list_movies(user["id"])
    title = prompt_non_empty_title("Enter new movie name: ")

    movie_details = movie_api.get_movie_details(title)

    if movie_details is None:
        print(f"Movie '{title}' could not be added.")
        return

    if movie_details["title"] in movies:
        print(f"Movie '{movie_details['title']}' already exists!")
        return

    storage.add_movie(
        user["id"],
        movie_details["title"],
        movie_details["year"],
        movie_details["rating"],
        movie_details["poster_url"],
        movie_details["imdb_id"],
        movie_details["country"],
        movie_details["country_flag"],
    )
    print(
        f"Movie '{movie_details['title']}' successfully added "
        f"to {user['name']}'s collection."
    )


def delete_movie(user):
    """Delete a movie from the storage."""
    movies = storage.list_movies(user["id"])
    title = prompt_non_empty_title("Enter movie name to delete: ")

    if title not in movies:
        print(f"Movie '{title}' doesn't exist!")
        return

    storage.delete_movie(user["id"], title)
    print(f"Movie '{title}' successfully deleted.")


def update_movie(user):
    """Add or update the note for an existing movie."""
    movies = storage.list_movies(user["id"])
    title = prompt_non_empty_title("Enter movie name: ")

    if title not in movies:
        print(f"Movie '{title}' doesn't exist!")
        return

    note = prompt_non_empty_title("Enter movie note: ")
    storage.update_movie(user["id"], title, note)
    print(f"Movie '{title}' successfully updated.")


def show_stats(user):
    """Display rating statistics for all movies."""
    movies = storage.list_movies(user["id"])

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


def search_movie(user):
    """Search movies by a partial title match."""
    movies = storage.list_movies(user["id"])

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


def sort_movies_by_rating(user):
    """Display movies sorted by rating."""
    movies = storage.list_movies(user["id"])

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


def sort_movies_by_year(user):
    """Display movies sorted by release year."""
    movies = storage.list_movies(user["id"])

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


def filter_movies(user):
    """Display movies filtered by rating and release year."""
    movies = storage.list_movies(user["id"])

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


def generate_movie_grid(movies):
    """Generate the HTML movie grid from stored movie data."""
    movie_items = []

    for title, details in sorted(movies.items(), key=lambda item: item[0]):
        poster_url = details.get("poster_url") or ""
        note = details.get("note") or ""
        imdb_id = details.get("imdb_id") or ""
        country = details.get("country") or ""
        country_flag = details.get("country_flag") or ""
        escaped_title = escape(title)
        movie_title = f"<div class=\"movie-title\">{escaped_title}</div>"
        movie_year = f"<div class=\"movie-year\">{details['year']}</div>"
        movie_country = (
            f"<div class=\"movie-country\" title=\"{escape(country)}\">"
            f"{escape(country_flag)} {escape(country)}</div>"
        )
        movie_rating = (
            f"<div class=\"movie-rating\">Rating: "
            f"{details['rating']:.1f}/10</div>"
        )
        movie_poster = (
            "                <img class=\"movie-poster\"\n"
            f"                     src=\"{escape(poster_url)}\"\n"
            f"                     title=\"{escape(note)}\"/>"
        )

        if imdb_id:
            imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
            movie_poster = (
                f"                <a href=\"{escape(imdb_url)}\"\n"
                "                   target=\"_blank\">\n"
                "    "
                f"{movie_poster.lstrip()}\n"
                "                </a>"
            )

        movie_items.append(
            "<li>\n"
            "            <div class=\"movie\">\n"
            f"{movie_poster}\n"
            f"                {movie_title}\n"
            f"                {movie_year}\n"
            f"                {movie_country}\n"
            f"                {movie_rating}\n"
            "            </div>\n"
            "        </li>"
        )

    return "\n        ".join(movie_items)


def get_user_website_path(user):
    """Return the generated website path for one user."""
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", user["name"]).strip("_")

    if not safe_name:
        safe_name = "user"

    return STATIC_DIR / f"{safe_name}.html"


def generate_website(user):
    """Generate an HTML website from the stored movies."""
    movies = storage.list_movies(user["id"])
    movie_grid = generate_movie_grid(movies)
    website_file_path = get_user_website_path(user)

    with TEMPLATE_FILE_PATH.open("r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    website_title = f"{user['name']}'s Movie App"
    website_content = template_content.replace(
        "__TEMPLATE_TITLE__",
        website_title,
    )
    website_content = website_content.replace(
        "__TEMPLATE_MOVIE_GRID__",
        movie_grid,
    )

    with website_file_path.open("w", encoding="utf-8") as website_file:
        website_file.write(website_content)

    print("Website was generated successfully.")


def handle_menu_choice(choice, user):
    """Execute the action that belongs to the chosen menu option."""
    if choice == "1":
        list_movies(user)
    elif choice == "2":
        add_movie(user)
    elif choice == "3":
        delete_movie(user)
    elif choice == "4":
        update_movie(user)
    elif choice == "5":
        show_stats(user)
    elif choice == "6":
        search_movie(user)
    elif choice == "7":
        sort_movies_by_rating(user)
    elif choice == "8":
        sort_movies_by_year(user)
    elif choice == "9":
        generate_website(user)
    elif choice == "10":
        filter_movies(user)
    elif choice == "11":
        return select_user()

    return user


def main():
    """Run the Movies application."""
    active_user = select_user()

    while True:
        print_menu()
        choice = prompt_menu_choice()

        if choice == "0":
            print("Bye!")
            break

        active_user = handle_menu_choice(choice, active_user)
        print()


if __name__ == "__main__":
    main()
