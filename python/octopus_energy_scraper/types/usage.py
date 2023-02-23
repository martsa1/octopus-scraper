"""Basic types for API responses etc."""

import enum
import typing as t
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import (  # pylint: disable = no-name-in-module
    BaseModel,
    Field,
    NonNegativeFloat,
    validator,
)


class EnergyType(enum.Enum):
    ELECTRICITY = enum.auto()
    GAS = enum.auto()

    def __str__(self) -> str:
        return self.name


class RawUsage(BaseModel):
    """Base Usage data model, as received from Octopus API."""

    consumption: NonNegativeFloat
    interval_start: datetime
    interval_end: datetime

    class Config:
        frozen = True

    @staticmethod
    def _coerce_to_utc(date: datetime) -> datetime:
        """Translates a timezone aware datetime to UTC."""
        return datetime.fromtimestamp(date.timestamp(), ZoneInfo("UTC"))

    @validator("interval_start")
    @classmethod
    def interval_start_is_utc(cls: t.Type["RawUsage"], value: datetime) -> datetime:
        """Ensure interval_start is stored as UTC."""
        return cls._coerce_to_utc(value)

    @validator("interval_end")
    @classmethod
    def interval_end_is_utc(cls: t.Type["RawUsage"], value: datetime) -> datetime:
        """Ensure interval_end is stored as UTC."""
        return cls._coerce_to_utc(value)

    @classmethod
    def from_raw_api_json(cls, raw_data: t.Mapping[str, t.Any]) -> t.Sequence["RawUsage"]:
        """Parse raw JSON API responses into sequence of RawUsage's."""
        if "results" not in raw_data:
            raise ValueError("no raw data to deserialise")

        results: t.MutableSequence["RawUsage"] = []
        for reading in raw_data["results"]:
            results.append(cls(**reading))

        return results

    def __lt__(self, other: t.Any) -> bool:
        if not isinstance(other, RawUsage):
            raise TypeError
        if self.consumption < other.consumption:
            return True
        if self.interval_start < other.interval_start:
            return True
        if self.interval_end < other.interval_end:
            return True
        return False


class ConsumptionAPIData(BaseModel):
    count: int
    next_: t.Optional[str] = Field(None, alias="next")
    previous: t.Optional[str] = None
    results: t.Sequence[RawUsage] = []
