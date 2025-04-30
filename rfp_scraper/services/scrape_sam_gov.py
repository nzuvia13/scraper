import asyncio
import datetime
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from pydantic import BaseModel, Field

from rfp_scraper import secrets


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
    city: City
    state: State | None = None
    zip: str | None = None
    country: Country | None = None


class Awardee(BaseModel):
    name: str
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
    fullName: str


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
    archiveType: str
    archiveDate: str
    typeOfSetAsideDescription: str | None = None
    typeOfSetAside: str | None = None
    responseDeadLine: str | None = None
    naicsCode: str | None = None
    naicsCodes: list[str] = Field(default_factory=list)
    classificationCode: str | None = None
    active: str
    award: Award | None = None
    pointOfContact: list[PointOfContact] | None = Field(default_factory=list)
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
    opportunitiesData: list[dict[str, Any]]  # Change to raw dict to avoid validation errors
    links: list[Link]


async def scrape_sam_gov(start_date: datetime.datetime, end_date: datetime.datetime) -> list[dict[str, Any]]:
    """Fetch opportunities data from SAM.gov API.

    Args:
        start_date: Start date for the search range
        end_date: End date for the search range

    Returns:
        List of opportunity data dictionaries
    """
    async with _build_authenticated_client() as client:
        all_opportunities: list[dict[str, Any]] = []
        api_max_limit = 1000
        search_params = {
            "limit": str(api_max_limit),
            "postedFrom": start_date.strftime(format="%m/%d/%Y"),
            "postedTo": end_date.strftime(format="%m/%d/%Y"),
        }
        # breakpoint()
        response = await client.get(url="/v2/search", params=search_params)

        if not response.is_success:
            raise Exception(f"Failed to scrape SAM.gov: {response.status_code} {response.text}")
        initial_response_data = SamGovSearchResponse.parse_obj(response.json())

        num_additional_pages = initial_response_data.totalRecords // api_max_limit
        all_opportunities.extend(initial_response_data.opportunitiesData)

        for offset_index in range(1, num_additional_pages + 1):
            next_page_offset = offset_index * api_max_limit
            response = await client.get(
                url="/v2/search",
                params={
                    **search_params,
                    "offset": str(next_page_offset),
                },
            )
            next_page_response_data = SamGovSearchResponse.parse_obj(response.json())
            all_opportunities.extend(next_page_response_data.opportunitiesData)

        return all_opportunities


if __name__ == "__main__":
    # Example usage with custom parameters
    result = asyncio.run(
        scrape_sam_gov(
            start_date=datetime.datetime(year=2023, month=1, day=1),
            end_date=datetime.datetime(year=2023, month=12, day=31),
        )
    )
    print(f"Retrieved {len(result)} opportunities")
