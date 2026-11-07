from datetime import date

import questionary
from rich.console import Console

from spotify_utils.config import DEFAULT_PAGE_SIZE
from spotify_utils.settings import ListeningMetric

console = Console()


def edit_settings(options):
    while True:
        start_date = (
            options.start_date.isoformat() if options.start_date else "All time"
        )
        end_date = options.end_date.isoformat() if options.end_date else "Present"
        metrics = ", ".join(sorted(metric.value for metric in options.metrics))
        page_size = options.page_size

        choices = [
            "Change start/end date",
            "Change metric(s)",
            "Change number of results",
            "Reset options",
            "Back",
        ]
        choice = questionary.select(
            f"Settings\n"
            f"Start date: {start_date}\n"
            f"End date: {end_date}\n"
            f"Metrics: {metrics}\n"
            f"Page size: {page_size}",
            choices=choices,
        ).ask()

        if choice is None or choice == "Back":
            break

        if choice == "Change start/end date":
            start_value = questionary.text(
                "Enter start date (YYYY-MM-DD, blank for all time):",
                default=options.start_date.isoformat() if options.start_date else "",
            ).ask()

            if start_value is None:
                continue

            end_value = questionary.text(
                "Enter end date (YYYY-MM-DD, blank for present):",
                default=options.end_date.isoformat() if options.end_date else "",
            ).ask()

            if end_value is None:
                continue

            try:
                start_date = date.fromisoformat(start_value) if start_value else None
                end_date = date.fromisoformat(end_value) if end_value else None

            except ValueError:
                console.print("[yellow]Invalid date. Use YYYY-MM-DD.[/yellow]")
                continue

            if (
                start_date is not None
                and end_date is not None
                and (start_date > end_date)
            ):
                continue

            options.start_date = start_date
            options.end_date = end_date

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
            options.end_date = None
            options.metrics = {ListeningMetric.TIME}
            options.page_size = DEFAULT_PAGE_SIZE
