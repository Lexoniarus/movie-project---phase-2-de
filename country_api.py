"""Helpers for retrieving country data from REST Countries."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


REST_COUNTRIES_URL = "https://restcountries.com/v3.1/name"


def get_country_flag(country_name):
    """Return a flag emoji for the given country name."""
    if not country_name:
        return ""

    first_country = country_name.split(",")[0].strip()
    request_url = (
        f"{REST_COUNTRIES_URL}/{quote(first_country)}"
        "?fields=flag"
    )

    try:
        with urlopen(request_url, timeout=10) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as error:
        print(f"HTTP error while fetching country flag: {error}")
        return ""
    except URLError as error:
        print(f"Network error while fetching country flag: {error}")
        return ""

    countries = json.loads(response_body)

    if not countries:
        return ""

    return countries[0].get("flag", "")
