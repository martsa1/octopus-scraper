import typing as t
from datetime import datetime

from pydantic import BaseModel, NonNegativeFloat  # pylint: disable = no-name-in-module


class RawUsage(BaseModel):
    """Base Usage data model, as received from Octopus API."""

    consumption: NonNegativeFloat
    interval_start: datetime
    interval_end: datetime

    @classmethod
    def from_raw_api_json(cls, raw_data: t.Mapping[str, t.Any]) -> t.Sequence["RawUsage"]:
        if "results" not in raw_data:
            raise ValueError("no raw data to deserialise")

        results: t.MutableSequence["RawUsage"] = []
        for reading in raw_data["results"]:
            results.append(cls(**reading))

        return results
