import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


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
