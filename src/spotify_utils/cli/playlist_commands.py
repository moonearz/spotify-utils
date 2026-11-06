import questionary
from rich.console import Console

from spotify_utils.cli.pagination import paginate
from spotify_utils.client import get_spotify_client
from spotify_utils.config import DEFAULT_MIN_PLAYS
from spotify_utils.history.analytics import load_history, song_skip_stats
from spotify_utils.playlists import (
    create_new_playlist,
    filter_playlist_by_skip_rate,
    filter_songs,
    get_playlist_tracks,
    get_user_playlists,
)
from spotify_utils.utils import format_playlist_track

console = Console()


def playlist_menu():
    sp = get_spotify_client()

    choices = [
        questionary.Choice(
            title="Manually filter playlists",
            value="filter_playlist",
        ),
        questionary.Choice(
            title="Filter playlist by skip rate",
            value="filter_by_skips",
        ),
        questionary.Choice(title="Back", value="back"),
    ]

    while True:
        util = questionary.select("Choose a utility:", choices=choices).ask()

        if util is None or util == "back":
            break

        if util == "filter_playlist":
            filter_playlist_command(sp)

        if util == "filter_by_skips":
            filter_playlist_by_skip_rate_command(sp)


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


def filter_playlist_by_skip_rate_command(sp):
    playlists = get_user_playlists(sp)

    if not playlists:
        console.print("No playlists found.")
        return

    choices = [
        questionary.Choice(
            title=playlist["name"],
            value=playlist,
        )
        for playlist in playlists
    ]

    playlist = questionary.select(
        "Select a playlist:",
        choices=choices,
    ).ask()

    if playlist is None:
        return

    value = questionary.text(
        "Maximum skip rate (0-100):",
        default="50",
    ).ask()

    if value is None:
        return

    try:
        threshold = float(value) / 100

        if not 0 <= threshold <= 1:
            raise ValueError
    except ValueError:
        console.print("Enter a percentage between 0 and 100")
        return

    value = questionary.text(
        "Minimum number of plays:",
        default=str(DEFAULT_MIN_PLAYS),
    ).ask()

    if value is None:
        return

    try:
        min_plays = int(value)

        if min_plays < 0:
            raise ValueError
    except ValueError:
        console.print("Min plays must be nonnegative")
        return

    history = load_history()
    stats = song_skip_stats(history)
    tracks = get_playlist_tracks(sp, playlist["id"])

    kept, removed = filter_playlist_by_skip_rate(
        tracks,
        stats,
        threshold,
        min_plays,
    )

    console.print(f"\n[bold]{playlist['name']}[/bold]")
    console.print(f"Original tracks: {len(tracks)}")
    console.print(f"Kept tracks: {len(kept)}")
    console.print(f"Removed tracks: {len(removed)}")

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "View kept tracks",
                "View removed tracks",
                "Create filtered playlist",
                "Back",
            ],
        ).ask()

        if choice is None or choice == "Back":
            break

        if choice == "View kept tracks":
            paginate(
                kept,
                formatter=format_playlist_track,
            )

        elif choice == "View removed tracks":
            paginate(
                removed,
                formatter=format_playlist_track,
            )

        elif choice == "Create filtered playlist":
            name = questionary.text(
                "New playlist name:",
                default=f"{playlist['name']}_filtered_{int(threshold * 100)}",
            ).ask()

            if not name:
                continue

            uris = [entry["item"]["uri"] for entry in kept]
            create_new_playlist(sp, name, uris)

            console.print(f"Created playlist: {name}")
            break
