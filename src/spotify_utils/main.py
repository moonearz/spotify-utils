import questionary

from spotify_utils.cli.history_commands import history_menu
from spotify_utils.cli.playlist_commands import playlist_menu
from spotify_utils.cli.settings import edit_settings
from spotify_utils.config import has_api_credentials, has_listening_history
from spotify_utils.settings import UtilOptions


def main():
    options = UtilOptions()
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
                disabled=None
                if (has_api_creds and has_history)
                else "Spotify API credentials and history required",
            ),
            questionary.Choice(
                "Change Settings",
                value="settings",
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
            history_menu(options)

        if command == "playlists":
            playlist_menu(options)

        if command == "settings":
            edit_settings(options)


if __name__ == "__main__":
    main()
