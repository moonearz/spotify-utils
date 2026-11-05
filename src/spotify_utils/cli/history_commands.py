import questionary
from rich.console import Console

from spotify_utils.history.history import (
    artist_distribution,
    load_history,
    most_played_artists,
)
from spotify_utils.visualization import plot_artist_distribution

console = Console()


def history_menu():
    history = load_history()

    choices = [
        questionary.Choice(
            title="Most played artists",
            value="most_played_artists",
        ),
        questionary.Choice(
            title="Listening statistics",
            value="listening_statistics",
        ),
        questionary.Choice(
            title="Back",
            value="back",
        ),
    ]

    while True:
        util = questionary.select("Choose a utility:", choices=choices).ask()

        if util is None or util == "back":
            break

        if util == "most_played_artists":
            most_played_artists_command(history)

        if util == "listening_statistics":
            artist_distribution_command(history)


def artist_distribution_command(history):
    artist_dist = artist_distribution(history)
    plot_artist_distribution(artist_dist)


def most_played_artists_command(history):
    artists = most_played_artists(history)

    console.print("\n[bold]Most played artists:[/bold]\n")

    for rank, (artist, count) in enumerate(artists, start=1):
        console.print(f"{rank}. {artist}: {count} listens")
