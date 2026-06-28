# RAWG Game Scraper

Small command-line tool to fetch game metadata from the RAWG API and export results to CSV and JSON.

## What it does

- Queries the RAWG REST API (`https://api.rawg.io/api/games`) and collects games.
- Supports simple filters: `--year`, `--genre`, and `--limit` (number of results).
- Writes `output.csv` and `output.json` in the current working directory.

## Requirements

- Python 3.10+ (or the system Python configured for this workspace)
- Dependencies listed in `requirements.txt` (`requests`, `python-dotenv`).

Install dependencies with:

```powershell
python -m pip install -r requirements.txt
```

## Environment

The script reads the RAWG API key from the environment variable `RAWG_API_KEY`. You can provide it with a `.env` file (the project uses `python-dotenv`) or by exporting the variable in your shell.

Example `.env` (do not commit):

```
RAWG_API_KEY=your_api_key_here
```

## Usage

Basic invocation:

```powershell
python scraper.py [--year YYYY] [--genre "genre1,genre2"] [--limit N]
```

Options:

- `--year`: four-digit year (e.g. `2006`). Filters games released during that year.
- `--genre`: comma-separated genres. Common aliases are mapped (for example `rpg` → `role-playing-games-rpg`).
- `--limit`: number of results to return (1–200, default 50).

Examples:

```powershell
# Fetch 30 RPGs from 2015
python scraper.py --genre rpg --year 2015 --limit 30

# Fetch 10 games across "action" and "indie"
python scraper.py --genre action,indie --limit 10
```

## Output

- `output.csv`: tabular export with columns `name`, `released`, `genres`, `metacritic`, `platforms`.
- `output.json`: pretty-printed JSON array of the same cleaned records.

## Notes on behavior and safety

- The script validates `--limit` (1–200) and `--year` (four digits). Invalid values produce user-friendly errors.
- Network requests use a timeout and will raise clear errors for network problems, timeouts, or API errors.
- Do not store API keys in source control. Use a `.env` file or CI secrets for automation.

## License

This project is licensed under the [MIT License](LICENSE).
