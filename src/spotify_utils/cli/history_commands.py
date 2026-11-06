from datetime import date
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
from spotify_utils.history.config import (
    DEFAULT_PAGE_SIZE,
    HistoryOptions,
    ListeningMetric,
)
from spotify_utils.visualization import plot_artist_distribution

console = Console()


def edit_history_options(options):
    while True:
        start_date = (
            options.start_date.isoformat() if options.start_date else "All time"
        )
        metrics = " ,".join(sorted(metric.value for metric in options.metrics))
        page_size = options.page_size

        choices = [
            "Change start date",
            "Change metric(s)",
            "Change number of results",
            "Reset options",
            "Back",
        ]
        choice = questionary.select(
            f"History settings\nStart date: {start_date}"
            f"\nMetrics: {metrics}"
            f"\nPage size: {page_size}",
            choices=choices,
        ).ask()

        if choice is None or choice == "Back":
            break

        if choice == "Change start date":
            value = questionary.text(
                "Enter start date (YYYY-MM-DD, blank for all time):",
                default=options.start_date.isoformat() if options.start_date else "",
            ).ask()

            if value is None:
                continue

            try:
                options.start_date = date.fromisoformat(value) if value else None
            except ValueError:
                print("Invalid date, use YYYY-MM-DD format")

        elif choice == "Change metric(s)":
            selected = questionary.checkbox(
                "Select listening metrics:",
                choices=[
                    questionary.Choice(
                        "Number of plays",
                        value=ListeningMetric.PLAYS,
                        checked=ListeningMetric.PLAYS in options.metrics,
                    ),
                    questionary.Choice(
                        "Time spent listening",
                        value=ListeningMetric.TIME,
                        checked=ListeningMetric.TIME in options.metrics,
                    ),
                ],
            ).ask()

            if selected:
                options.metrics = set(selected)
            elif selected == []:
                print("Select at least one metric")

        elif choice == "Change number of results":
            value = questionary.text(
                "Number of results:",
                default=str(options.page_size),
            ).ask()

            if value is None:
                continue

            try:
                n = int(value)
                if n < 1:
                    raise ValueError
                options.page_size = n
            except ValueError:
                console.print("Enter a number > 0")

        elif choice == "Reset options":
            options.start_date = None
            options.metrics = {ListeningMetric.TIME}
            options.page_size = DEFAULT_PAGE_SIZE


def history_menu():
    history = load_history()
    options = HistoryOptions()

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
            title="Change Settings",
            value="change_settings",
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

        if util == "change_settings":
            edit_history_options(options)
            continue

        filtered_history = filter_history(history, options.start_date)

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
        formatter=lambda item: f"{item[0][0]} by {item[0][1]}: {item[1]:.1%}",
    )
