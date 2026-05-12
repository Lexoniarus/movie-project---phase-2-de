# Movie Project Phase 2

This is a command line Movies application built with Python. It stores movie
data in SQLite through SQLAlchemy, retrieves movie details from the OMDb API,
and can generate a simple HTML website from the saved movies.

## Features

- List saved movies
- Add movies by title through the OMDb API
- Delete and update saved movies
- Show statistics, search, sort, and filter movies
- Generate a static movie website with posters
- Create separate user profiles with individual movie collections
- Add personal notes to movies and show them as poster hover text
- Show movie ratings on the generated website
- Link movie posters to their IMDb pages
- Show country flags next to movies on the generated website
- Show a movie count and average rating summary on the website

## Setup

Install the project dependency:

```powershell
pip install -r requirements.txt
```

Set your OMDb API key before adding movies from the API:

```powershell
$env:OMDB_API_KEY='your_api_key'
```

## Usage

Start the app from the project root:

```powershell
python movies.py
```

When the app starts, select an existing user profile or create a new one. All
movie commands work only with the active user's collection.

Use menu option `9` to generate the website. The generated file is written to
`_static/<user-name>.html`.

## Project Structure

- `movies.py`: main command line application
- `movie_api.py`: OMDb API helper functions
- `storage/`: storage modules for JSON and SQL storage
- `data/`: local SQLite database directory
- `_static/`: website template and CSS files
