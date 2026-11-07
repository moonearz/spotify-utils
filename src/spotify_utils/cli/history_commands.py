from functools import partial

import questionary
from rich.console import Console

from spotify_utils.cli.pagination import paginate
from spotify_utils.history.analytics import (
    artist_distribution,
    filter_history,
    load_history,
    most_played_artists,
    most_skipped_songs,
)
from spotify_utils.settings import (
    ListeningMetric,
)
from spotify_utils.visualization import plot_artist_distribution

console = Console()


def history_menu(options):
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
            title="Most skipped songs",
            value="most_skipped_songs",
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

        filtered_history = filter_history(history, options.start_date, options.end_date)

        if util == "most_played_artists":
            most_played_artists_command(filtered_history, options)

        if util == "listening_statistics":
            artist_distribution_command(filtered_history, options)

        if util == "most_skipped_songs":
            most_skipped_song_command(filtered_history, options)


def artist_distribution_command(history, options):
    for metric in sorted(options.metrics):
        artist_dist = artist_distribution(history, metric, options.page_size)

        console.print(f"\nMost played artists by {metric.value}:\n")
        plot_artist_distribution(artist_dist)


def format_artist(item, metric):
    artist, count = item
    if metric == ListeningMetric.TIME:
        return f"{artist}: {count / 3_600_000:.1f} hours"
    else:
        return f"{artist}: {count:,} listens"


def most_played_artists_command(history, options):
    for metric in sorted(options.metrics):
        artists = most_played_artists(history, metric)

        console.print(f"\n[bold]Most played artists by {metric.value}:[/bold]\n")

        paginate(
            artists,
            page_size=options.page_size,
            formatter=partial(format_artist, metric=metric),
        )


def most_skipped_song_command(history, options):
    most_skipped = most_skipped_songs(history)

    console.print("\n[bold]Most skipped songs:[/bold]\n")
    paginate(
        most_skipped,
        page_size=options.page_size,
        formatter=lambda item: (
            f"{item[1]['display_name'][0]} by "
            f"{item[1]['display_name'][1]}: "
            f"{item[1]['skip_rate']:.1%}"
        ),
    )
