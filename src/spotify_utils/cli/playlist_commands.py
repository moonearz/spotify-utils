import questionary
from rich.console import Console

from spotify_utils.client import get_spotify_client
from spotify_utils.playlists import (
    create_new_playlist,
    filter_songs,
    get_user_playlists,
)

console = Console()


def playlist_menu():
    sp = get_spotify_client()

    choices = [
        questionary.Choice(
            title="Manually filter playlists",
            value="filter_playlists",
        ),
        questionary.Choice(title="Back", value="back"),
    ]

    while True:
        util = questionary.select("Choose a utility:", choices=choices).ask()

        if util is None or util == "back":
            break

        if util == "filter_playlist":
            filter_playlist_command(sp)


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
