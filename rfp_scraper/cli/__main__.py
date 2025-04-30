"""
https://typer.tiangolo.com/tutorial/
"""

import asyncio
from datetime import datetime

import typer

from rfp_scraper.services import scrape_sam_gov

app = typer.Typer(no_args_is_help=True)

scrape = typer.Typer(no_args_is_help=True)
app.add_typer(scrape, name="scrape")

DEFAULT_START_DATE = datetime(year=2025, month=4, day=28)
DEFAULT_END_DATE = datetime(year=2025, month=4, day=29)


@scrape.command(name="sam")
def scrape_sam_gov_command(start: datetime = DEFAULT_START_DATE, end: datetime = DEFAULT_END_DATE) -> None:
    asyncio.get_event_loop().run_until_complete(
        scrape_sam_gov.run_scraping(
            start_date=start,
            end_date=end,
        )
    )  # pyright: ignore[reportUnusedCallResult]


if __name__ == "__main__":
    app()
