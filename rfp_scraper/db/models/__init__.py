from __future__ import annotations

import datetime
import enum
from typing import Literal

from pydantic import UUID6
from sqlmodel import Field, Relationship, SQLModel
from uuid6 import uuid6


class ScrapingSource(str, enum.Enum):
    SAMMGOV = "sammgov"


class OpportunityRun(SQLModel, table=True):
    __tablename__: Literal["opportunity_run"] = "opportunity_run"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: UUID6 | None = Field(default_factory=uuid6, primary_key=True)
    created_at: datetime.datetime = Field(default=datetime.datetime.now(tz=datetime.UTC), nullable=False)
    last_updated: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC), nullable=False
    )
    source: ScrapingSource
    run_date: datetime.datetime
    scrapes: list[SamGovScrape] = Relationship(back_populates="opportunity_run")


class SamGovScrape(SQLModel, table=True):
    __tablename__: Literal["opportunity_scrapes"] = "opportunity_scrapes"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: UUID6 | None = Field(default_factory=uuid6, primary_key=True)
    created_at: datetime.datetime = Field(default=datetime.datetime.now(tz=datetime.UTC), nullable=False)
    last_updated: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC), nullable=False
    )
    opportunity_run_id: UUID6 = Field(foreign_key="opportunity_run.id")
