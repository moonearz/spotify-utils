import questionary

from spotify_utils.cli.history_commands import history_menu
from spotify_utils.cli.playlist_commands import playlist_menu
from spotify_utils.config import has_api_credentials, has_listening_history


def main():
    while True:
        has_api_creds = has_api_credentials()
        has_history = has_listening_history()

        choices = [
            questionary.Choice(
                "Listening Statistics",
                value="history",
                disabled=None
                if has_history
                else "Listening history in data dir required",
            ),
            questionary.Choice(
                "Playlist Management",
                value="playlists",
                disabled=None if has_api_creds else "Spotify API credentials required",
            ),
            questionary.Choice(
                "Quit",
                value="quit",
            ),
        ]
        command = questionary.select("Spotify Utilities", choices=choices).ask()

        if command is None or command == "quit":
            break

        if command == "history":
            history_menu()

        if command == "playlists":
            playlist_menu()


if __name__ == "__main__":
    main()
