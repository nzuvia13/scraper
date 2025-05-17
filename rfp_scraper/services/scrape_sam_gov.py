import datetime
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from rfp_scraper import logging, secrets

from . import output_directories


@asynccontextmanager
async def _build_authenticated_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an authenticated HTTP client for SAM.gov API with default query parameters."""
    params = {
        "api_key": secrets.SAM_GOV_API_KEY,
    }

    # Create client with base URL and default params
    client = httpx.AsyncClient(
        base_url="https://api.sam.gov/opportunities",
        params=params,
    )

    try:
        yield client
    finally:
        await client.aclose()


class City(BaseModel):
    name: str


class State(BaseModel):
    name: str | None = None


class Country(BaseModel):
    code: str | None = None
    name: str | None = None


class Location(BaseModel):
    city: City | None = None
    state: State | None = None
    zip: str | None = None
    country: Country | None = None


class Awardee(BaseModel):
    name: str | None = None
    location: Location | None = None
    ueiSAM: str | None = None
    cageCode: str | None = None


class Award(BaseModel):
    date: str | None = None
    number: str | None = None
    amount: str | None = None
    awardee: Awardee | None = None


class PointOfContact(BaseModel):
    fax: str | None = None
    type: str
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    fullName: str | None = None


class OfficeAddress(BaseModel):
    zipcode: str | None = None
    city: str | None = None
    countryCode: str | None = None
    state: str | None = None


class Link(BaseModel):
    rel: str
    href: str


class SamGovOpportunity(BaseModel):
    noticeId: str
    title: str
    solicitationNumber: str
    fullParentPathName: str
    fullParentPathCode: str
    postedDate: str
    type: str
    baseType: str
    archiveType: str | None = None
    archiveDate: str | None = None
    typeOfSetAsideDescription: str | None = None
    typeOfSetAside: str | None = None
    responseDeadLine: str | None = None
    naicsCode: str | None = None
    naicsCodes: list[str] = Field(default_factory=list)
    classificationCode: str | None = None
    active: str
    award: Award | None = None
    pointOfContact: list[PointOfContact] | None = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    description: str
    organizationType: str
    officeAddress: OfficeAddress | None = None
    placeOfPerformance: Any | None = None
    additionalInfoLink: str | None = None
    uiLink: str
    links: list[Link]
    resourceLinks: Any | None = None


class SamGovSearchResponse(BaseModel):
    totalRecords: int
    limit: int
    offset: int
    opportunitiesData: list[SamGovOpportunity]  # Change to raw dict to avoid validation errors
    links: list[Link]


async def run_scraping(start_date: datetime.datetime, end_date: datetime.datetime) -> list[SamGovOpportunity]:
    """Fetch opportunities data from SAM.gov API.

    Args:
        start_date: Start date for the search range
        end_date: End date for the search range

    Returns:
        List of opportunity data dictionaries
    """
    logger = logging.build_logger(name=f"{__name__}.{run_scraping.__name__}")
    logger.info("Starting to scrape SAM.gov opportunities", start_date=start_date, end_date=end_date)
    async with _build_authenticated_client() as client:
        all_opportunities: list[SamGovOpportunity] = []
        api_max_limit = 1000
        search_params = {
            "limit": str(api_max_limit),
            "postedFrom": start_date.strftime(format="%m/%d/%Y"),
            "postedTo": end_date.strftime(format="%m/%d/%Y"),
        }
        # breakpoint()
        response = await client.get(url="/v2/search", params=search_params)

        logger.info("SAM.gov search response", status=response.status_code)

        if not response.is_success:
            raise Exception(f"Failed to scrape SAM.gov: {response.status_code} {response.text}")

        initial_response_json = response.json()
        try:
            initial_response_data = SamGovSearchResponse.model_validate(initial_response_json)
        except ValidationError as e:
            logger.error("Validation errors", errors=e.errors(), response_json=initial_response_json)
            raise e

        num_additional_pages = initial_response_data.totalRecords // api_max_limit
        all_opportunities.extend(initial_response_data.opportunitiesData)

        logger.info(
            "SAM.gov search pagination determination",
            num_additional_pages=num_additional_pages,
            api_max_limit=api_max_limit,
            cnt_records=initial_response_data.totalRecords,
        )

        for offset_index in range(1, num_additional_pages + 1):
            next_page_offset = offset_index * api_max_limit
            logger.info(
                "SAM.gov search pagination",
                offset_index=offset_index,
                num_additional_pages=num_additional_pages,
                next_page_offset=next_page_offset,
            )
            response = await client.get(
                url="/v2/search",
                params={
                    **search_params,
                    "offset": str(next_page_offset),
                },
            )
            next_page_response_data = SamGovSearchResponse.model_validate(response.json())
            all_opportunities.extend(next_page_response_data.opportunitiesData)

        logger.info("SAM.gov search pagination complete", cnt_total_records=len(all_opportunities))
        return all_opportunities


def write_scraping_outputs(
    *, start_time: datetime.datetime, end_time: datetime.datetime, opportunities: list[SamGovOpportunity]
) -> None:
    """Write the scraping outputs to the SamGovScrapes output directory."""
    logger = logging.build_logger(name=f"{__name__}.{write_scraping_outputs.__name__}")
    logger.info("Writing scraping outputs", cnt_opportunities=len(opportunities))
    adapter = TypeAdapter(list[SamGovOpportunity])
    opportunities_json_contents = adapter.dump_json(opportunities).decode("utf-8")
    if not output_directories.SAM_GOV_SCRAPES_DIR.exists():
        output_directories.SAM_GOV_SCRAPES_DIR.mkdir(parents=True, exist_ok=True)

    start_time_formatted = start_time.strftime(format="%Y-%m-%d")
    start_time_unix = int(start_time.timestamp())
    end_time_unix = int(end_time.timestamp())
    filename = f"{start_time_formatted}__{start_time_unix}__{end_time_unix}.json"
    output_file_path = output_directories.SAM_GOV_SCRAPES_DIR / filename

    with open(output_file_path, mode="w") as f:
        f.write(opportunities_json_contents)  # pyright: ignore[reportUnusedCallResult]

    logger.info(
        "Scraping outputs written",
        output_file_path=output_file_path,
        start_time_formatted=start_time_formatted,
        start_time_unix=start_time_unix,
        end_time_unix=end_time_unix,
    )
