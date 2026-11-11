from datetime import datetime
from functools import partial

import questionary
from rich.console import Console

from spotify_utils.cli.pagination import paginate
from spotify_utils.history.analytics import (
    artist_distribution,
    diversity_index,
    filter_history,
    load_history,
    most_played_artists,
    most_skipped_songs,
    obsessiveness_index,
    total_listening,
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
            title="Artist listening statistics",
            value="listening_statistics",
        ),
        questionary.Choice(
            title="Most skipped songs",
            value="most_skipped_songs",
        ),
        questionary.Choice(
            title="Summary Statistics",
            value="summary_statistics",
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

        if util == "summary_statistics":
            summary_statistics_command(filtered_history, options)


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


def summary_statistics_command(history, options):
    if not history:
        console.print("[yellow]No listening history available.[/yellow]")
        return

    total_ms = total_listening(history, ListeningMetric.TIME)
    total_hours = total_ms / 3_600_000

    dates = [
        datetime.fromisoformat(record["ts"].replace("Z", "+00:00")).date()
        for record in history
    ]

    start_date = min(dates)
    end_date = max(dates)
    num_days = (end_date - start_date).days + 1
    avg_hours = total_hours / num_days

    console.print("\n[bold]Listening Summary[/bold]")
    console.print(
        f"[dim]Covering {start_date:%B %d, %Y} - "
        f"{end_date:%B %d, %Y} ({num_days:,} days)[/dim]\n"
    )

    console.print("\n[bold]Listening Summary[/bold]\n")

    console.print(f"Total listening time:       {total_hours:,.1f} hours")
    console.print(f"Average listening per day:  {avg_hours:.2f} hours")

    for metric in options.metrics:
        diversity = diversity_index(history, metric)
        obsessiveness = obsessiveness_index(history, metric)
        console.print(f"\n[bold]{metric.value.title()}[/bold]")
        console.print(f"Diversity index:           {diversity:.2f}")
        console.print(f"Obsessiveness index:       {obsessiveness:.2f}")
