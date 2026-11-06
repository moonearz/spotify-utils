import questionary
from rich.console import Console

from spotify_utils.config import DEFAULT_PAGE_SIZE

console = Console()


def paginate(items, page_size=DEFAULT_PAGE_SIZE, formatter=str):
    if not items:
        console.print("No results found.")
        return

    page = 0
    total_pages = (len(items) + page_size - 1) // page_size

    while True:
        start = page * page_size
        end = start + page_size

        console.print(f"\n[bold]Page {page + 1} of {total_pages}[/bold]\n")

        for i, item in enumerate(items[start:end], start=start + 1):
            console.print(f"{i}. {formatter(item)}")

        choices = []

        if page > 0:
            choices.append("Previous page")

        if page < total_pages - 1:
            choices.append("Next page")

        choices.append("Back")

        choice = questionary.select(
            "Navigate results:",
            choices=choices,
        ).ask()

        if choice == "Next page":
            page += 1
        elif choice == "Previous page":
            page -= 1
        else:
            break
