"""
https://typer.tiangolo.com/tutorial/
"""

import asyncio
from datetime import datetime, timedelta

import typer

from rfp_scraper.services import scrape_sam_gov

app = typer.Typer(no_args_is_help=True)

scrape = typer.Typer(no_args_is_help=True)
app.add_typer(scrape, name="scrape")

DEFAULT_END_DATE = datetime.now()
DEFAULT_START_DATE = DEFAULT_END_DATE - timedelta(days=1)


@scrape.command(name="sam")
def scrape_sam_gov_command(start: datetime = DEFAULT_START_DATE, end: datetime = DEFAULT_END_DATE) -> None:
    sam_gov_opportunities = asyncio.get_event_loop().run_until_complete(
        scrape_sam_gov.run_scraping(
            start_date=start,
            end_date=end,
        )
    )
    scrape_sam_gov.write_scraping_outputs(start_time=start, end_time=end, opportunities=sam_gov_opportunities)


if __name__ == "__main__":
    app()
