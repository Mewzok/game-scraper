import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("RAWG_API_KEY")

if not API_KEY:
    print("Error: Could not find RAWG_API_KEY in your environment!")
    exit()

def display_games(games_list):
    for game in games_list:
        # extract names from genres and platforms
        genres = [g['name'] for g in game.get('genres', [])]
        platforms = [p['platform']['name'] for p in game.get('platforms', [])]

        print(
            f"Title: {game['name']} | "
            f"Released: {game['released']} | "
            f"Genres: {', '.join(genres)} | "
            f"Metacritic Rating: {game['metacritic']} | "
            f"Platforms: {', '.join(platforms)}\n"
        )

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

    display_games(game_list)

if __name__ == "__main__":
    main()