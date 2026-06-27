import requests
import time
import os
import csv
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("RAWG_API_KEY")

if not API_KEY:
    print("Error: Could not find RAWG_API_KEY in your environment!")
    exit()

def build_cleaned_games(games_list):
    cleaned_games = []

    for game in games_list:
        # extract names from genres and platforms
        genres = ", ".join([g['name'] for g in game.get('genres', [])])
        platforms = ", ".join([p['platform']['name'] for p in game.get('platforms', [])])

        cleaned_games.append({
            "name": game.get('name', 'Unknown'), 
            "released": game.get('released', 'N/A'), 
            "genres": genres, 
            "metacritic": game.get('metacritic', 'N/A'), 
            "platforms": platforms
        })

    return cleaned_games

def write_csv(cleaned_games):
    field_names = ["name", "released", "genres", "metacritic", "platforms"]

    with open("output.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(cleaned_games)

def write_json(games_dict):
    with open("output.json", "w") as file:
        json.dump(games_dict, file, indent=4)

def main():
    search_url = "https://api.rawg.io/api/games"
    game_list = []
    result_limit = 50
    first_page = True

    query_params = {
        "key": API_KEY,
        "page_size": 40
    }

    while search_url and len(game_list) < result_limit:
        try:
            if first_page:
                response = requests.get(search_url, params=query_params)
                first_page = False
            else:
                response = requests.get(search_url, params=None)

            if response.status_code == 200:
                data = response.json()

                for game in data.get("results", []):
                    if len(game_list) < result_limit:
                        game_list.append(game)

                search_url = data['next']
            else:
                print(f"Error: Received status code {response.status_code}")
                print(response.json)

        except Exception as exc:
            print(f"An error occured: {exc}")
        
        
        time.sleep(2)

    cleaned_games = build_cleaned_games(game_list)
    write_csv(cleaned_games)
    write_json(cleaned_games)

if __name__ == "__main__":
    main()