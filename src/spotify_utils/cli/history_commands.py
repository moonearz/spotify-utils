from datetime import date

import questionary
from rich.console import Console

from spotify_utils.history.analytics import (
    artist_distribution,
    filter_history,
    load_history,
    most_played_artists,
)
from spotify_utils.history.config import HistoryOptions, ListeningMetric
from spotify_utils.visualization import plot_artist_distribution

console = Console()


def edit_history_options(options):
    while True:
        start_date = (
            options.start_date.isoformat() if options.start_date else "All time"
        )
        metrics = " ,".join(sorted(metric.value for metric in options.metrics))

        choices = [
            "Change start date",
            "Change metric(s)",
            "Reset options",
            "Back",
        ]
        choice = questionary.select(
            f"History settings\nStart date: {start_date}\nMetrics: {metrics}",
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

        elif choice == "Reset options":
            options.start_date = None
            options.metrics = {ListeningMetric.TIME}


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


def artist_distribution_command(history, options):
    for metric in sorted(options.metrics):
        artist_dist = artist_distribution(history, metric)

        console.print(f"\nMost played artists by {metric.value}:\n")
        plot_artist_distribution(artist_dist)


def most_played_artists_command(history, options):
    for metric in sorted(options.metrics):
        artists = most_played_artists(history, metric)

        console.print(f"\n[bold]Most played artists by {metric.value}:[/bold]\n")

        for rank, (artist, count) in enumerate(artists, start=1):
            if metric == ListeningMetric.TIME:
                console.print(f"{rank}. {artist}: {count / 3_600_000:.1f} hours")
            else:
                console.print(f"{rank}. {artist}: {count} listens")
