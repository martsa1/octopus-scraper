import typing as t
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, NonNegativeFloat, validator  # pylint: disable = no-name-in-module


class RawUsage(BaseModel):
    """Base Usage data model, as received from Octopus API."""

    consumption: NonNegativeFloat
    interval_start: datetime
    interval_end: datetime

    @staticmethod
    def _coerce_to_utc(date: datetime) -> datetime:
        """Translates a timezone aware datetime to UTC."""
        return datetime.fromtimestamp(date.timestamp(), ZoneInfo("UTC"))

    @validator("interval_start")
    @classmethod
    def interval_start_is_utc(cls: t.Type["RawUsage"], value: datetime) -> datetime:
        return cls._coerce_to_utc(value)

    @validator("interval_end")
    @classmethod
    def interval_end_is_utc(cls: t.Type["RawUsage"], value: datetime) -> datetime:
        return cls._coerce_to_utc(value)

    @classmethod
    def from_raw_api_json(cls, raw_data: t.Mapping[str, t.Any]) -> t.Sequence["RawUsage"]:
        if "results" not in raw_data:
            raise ValueError("no raw data to deserialise")

        results: t.MutableSequence["RawUsage"] = []
        for reading in raw_data["results"]:
            results.append(cls(**reading))

        return results
