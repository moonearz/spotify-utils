import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_PAGE_SIZE = 10
DEFAULT_MIN_PLAYS = 20
DEFAULT_WINDOW_SIZE = 50


def has_api_credentials() -> bool:
    return all(
        [
            os.getenv("SPOTIPY_CLIENT_ID"),
            os.getenv("SPOTIPY_CLIENT_SECRET"),
            os.getenv("SPOTIPY_REDIRECT_URI"),
        ]
    )


def has_listening_history() -> bool:
    return any(DATA_DIR.glob("Streaming_History_*.json"))
