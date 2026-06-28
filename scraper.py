import argparse
import csv
import json
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

GENRE_SLUGS = {
    "rpg": "role-playing-games-rpg",
    "fps": "shooter",
    "sim": "simulation",
    "mmo": "massively-multiplayer",
    "board games": "board-games",
    "board": "board-games",
    "tabletop": "board-games,card",
}


def get_api_key():
    return os.environ.get("RAWG_API_KEY")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Obtain and export a list of games and their details."
    )
    parser.add_argument(
        "--year",
        type=validate_year,
        help="The full year the games released (e.g. 2006)",
    )
    parser.add_argument(
        "--genre",
        type=str,
        help="The genre or genres of the desired games separated by commas (e.g. indie,action)",
    )
    parser.add_argument(
        "--limit",
        type=validate_limit,
        default=50,
        help="The number of results to obtain (default 50, min 1, max 200)",
    )
    return parser.parse_args()


def validate_limit(value):
    try:
        limit = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("Limit must be an integer.") from exc

    if not 1 <= limit <= 200:
        raise argparse.ArgumentTypeError("Limit must be between 1 and 200.")

    return limit


def validate_year(value):
    try:
        year = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("Year must be a valid integer.") from exc
    
    current_year = datetime.now().year

    if not (1970 <= year <= current_year):
        raise argparse.ArgumentTypeError(f"Year must be between 1970 and {current_year}.")

    return year


def parse_year_to_dates(value):
    year = int(str(value))
    return f"{year:04d}-01-01,{year:04d}-12-31"


def normalize_genres(value):
    if value is None:
        return None

    parts = [part.strip() for part in str(value).split(",") if part.strip()]
    if not parts:
        raise ValueError("Genre filter cannot be empty.")

    normalized_parts = []
    for part in parts:
        normalized_parts.append(GENRE_SLUGS.get(part.lower(), part.lower()))

    return ",".join(normalized_parts)


def build_cleaned_games(games_list):
    cleaned_games = []

    for game in games_list:
        genres = ", ".join(
            g["name"]
            for g in game.get("genres") or []
            if g and "name" in g    
        )
        platforms = ", ".join(
            p["platform"]["name"]
            for p in game.get("platforms") or []
            if p and "platform" in p and "name" in p["platform"]
        )

        cleaned_games.append(
            {
                "name": game.get("name", "Unknown"),
                "released": game.get("released", "N/A"),
                "genres": genres,
                "metacritic": game.get("metacritic", "N/A"),
                "platforms": platforms,
            }
        )

    return cleaned_games


def write_csv(cleaned_games):
    field_names = ["name", "released", "genres", "metacritic", "platforms"]

    with open("output.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(cleaned_games)


def write_json(games_dict):
    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(games_dict, file, indent=4)


def build_query_params(api_key, year=None, genre=None):
    query_params = {"key": api_key, "page_size": 40}

    if year is not None:
        query_params["dates"] = parse_year_to_dates(year)

    if genre:
        query_params["genres"] = normalize_genres(genre)

    return query_params


def fetch_games(api_key, limit, year=None, genre=None):
    search_url = "https://api.rawg.io/api/games"
    game_list = []
    query_params = build_query_params(api_key, year=year, genre=genre)
    next_url = search_url

    while next_url and len(game_list) < limit:
        try:
            response = requests.get(next_url, params=query_params if next_url == search_url else None, timeout=10)
            response.raise_for_status()
            data = response.json()

            for game in data.get("results", []):
                if len(game_list) < limit:
                    game_list.append(game)
                else:
                    break

            next_url = data.get("next")
            if next_url and len(game_list) < limit:
                time.sleep(2)
                query_params = None # set to none to avoid sending duplicate params in url
        except requests.Timeout as exc:
            raise RuntimeError("The RAWG API request timed out. Please try again later.") from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else "Unknown"
            raise RuntimeError(f"RAWG API request failed with status code {status_code}.") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"Network error while calling RAWG API: {exc}") from exc
        except ValueError as exc:
            raise RuntimeError("RAWG API returned invalid JSON.") from exc

    return game_list


def main():
    args = parse_arguments()
    api_key = get_api_key()

    if not api_key:
        print("Error: Could not find RAWG_API_KEY in your environment or .env file.")
        return 1

    try:
        games = fetch_games(api_key, limit=args.limit, year=args.year, genre=args.genre)
    except ValueError as exc:
        print(f"Configuration Error: {exc}")
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    try:
        cleaned_games = build_cleaned_games(games)
        
        print("Saving data to files...")
        write_csv(cleaned_games)
        write_json(cleaned_games)
        print(f"Successfully fetched {len(cleaned_games)} games.")
        return 0
    
    except PermissionError:
        print("Error: Permission denied. Please close 'output.csv' or 'output.json' if they are open in another program.")
        return 1
    except OSError as exc:
        print(f"System Error saving files: {exc.strerror}")
        return 1
    except Exception as exc:
        print(f"An unexpected error occurred while saving: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())