import questionary
from rich.console import Console

from spotify_utils.client import get_spotify_client
from spotify_utils.config import has_api_credentials, has_listening_history
from spotify_utils.history import artist_distribution, load_history, most_played_artists
from spotify_utils.playlists import (
    create_new_playlist,
    filter_songs,
    get_user_playlists,
)
from spotify_utils.visualization import plot_artist_distribution

console = Console()


def artist_distribution_command():
    history = load_history()
    artist_dist = artist_distribution(history)
    plot_artist_distribution(artist_dist)


def most_played_artists_command():
    history = load_history()
    artists = most_played_artists(history)

    console.print("\n[bold]Most played artists:[/bold]\n")

    for rank, (artist, count) in enumerate(artists, start=1):
        console.print(f"{rank}. {artist}: {count} listens")


def filter_playlist_command(sp):
    playlists = get_user_playlists(sp)

    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    choices = [
        questionary.Choice(title=playlist["name"], value=playlist["id"])
        for playlist in playlists
    ]
    playlist_id = questionary.select(
        "Choose a playlist to filter:", choices=choices
    ).ask()
    if playlist_id is None:
        return

    new_name = questionary.text("Enter a new playlist name:").ask()

    if new_name is None:
        return

    new_name = new_name.strip()

    if not new_name:
        console.print("[yellow]Playlist name cannot be empty.[/yellow]")
        return

    kept_songs = filter_songs(sp, playlist_id)

    if kept_songs is None:
        console.print("[yellow]Filtering cancelled.[/yellow]")
        return

    playlist = create_new_playlist(sp, new_name, kept_songs)

    console.print(
        f"\n[green]Created '{playlist['name']}' with {len(kept_songs)} entries.[/green]"
    )


def main():
    while True:
        has_api_creds = has_api_credentials()
        has_history = has_listening_history()

        choices = [
            questionary.Choice(
                "Filter playlist",
                value="filter playlist",
                disabled=None if has_api_creds else "Spotify API credentials required",
            ),
            questionary.Choice(
                "Most played artists",
                value="most played artists",
                disabled=None
                if has_history
                else "Listening history in data dir required",
            ),
            questionary.Choice(
                "Artist distribution",
                value="artist distribution",
                disabled=None
                if has_history
                else "Listening history in data dir required",
            ),
            questionary.Choice(
                "Quit",
                value="quit",
            ),
        ]
        command = questionary.select("Spotify Utilities", choices=choices).ask()

        if command is None or command == "quit":
            break

        if command == "filter a playlist":
            sp = get_spotify_client()
            filter_playlist_command(sp)

        if command == "most played artists":
            most_played_artists_command()

        if command == "artist distribution":
            artist_distribution_command()


if __name__ == "__main__":
    main()
