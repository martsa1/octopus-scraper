"""Basic flat-file data cache."""

import typing as t
from pathlib import Path

from pydantic import BaseModel, Field  # pylint: disable = no-name-in-module

from ..types.electricity import RawElectricityUsage
from ..types.gas import RawGasUsage


class UsageData(BaseModel):  # pylint: disable = too-few-public-methods
    """Consumption data."""

    electricity_usage: t.MutableSequence[RawElectricityUsage] = []
    gas_usage: t.MutableSequence[RawGasUsage] = []


class FileCache(BaseModel):
    """Pydantic model used to store data to a flat file format (JSON)."""

    cache_path: Path
    usage_data: UsageData = Field(default_factory=UsageData)

    def load(self) -> None:
        """Deserialise cache from disk."""
        if not self.cache_path.exists():
            return
        disk_data = self.parse_file(self.cache_path)
        self.usage_data = disk_data.usage_data

    def flush(self) -> None:
        """Flush cache to disk."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.touch()
        self.cache_path.write_text(self.json())
