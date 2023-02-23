"""Basic flat-file data cache."""

import logging
import typing as t
from pathlib import Path
from types import TracebackType

from pydantic import BaseModel, Field, PrivateAttr  # pylint: disable = no-name-in-module

from ..types.usage import EnergyType, RawUsage
from .base import CacheBase

LOG = logging.getLogger(__name__)


class UsageData(BaseModel):  # pylint: disable = too-few-public-methods
    """Consumption data."""

    electricity_usage: t.MutableSequence[RawUsage] = []
    gas_usage: t.MutableSequence[RawUsage] = []
    _uniq_electricity: t.Set[RawUsage] = PrivateAttr(set())
    _uniq_gas: t.Set[RawUsage] = PrivateAttr(set())


class FileCache(CacheBase, BaseModel):
    """Pydantic model used to store data to a flat file format (JSON)."""

    cache_path: Path = Path()
    usage_data: UsageData = Field(default_factory=UsageData)

    def load(self) -> None:
        """Deserialise cache from disk."""
        if not self.cache_path.exists():
            LOG.info("Cannot load from disk, no cache present yet.")
            return

        disk_data = self.parse_file(self.cache_path)
        self.usage_data = disk_data.usage_data
        self.usage_data._uniq_electricity = set(self.usage_data.electricity_usage)
        self.usage_data._uniq_gas = set(self.usage_data.gas_usage)

    def flush(self) -> None:
        """Flush cache to disk."""
        LOG.debug(f"Creating/updating {str(self.cache_path)}")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.touch()

        # transfer in-memory sets to lists to be flushed to disk... this is messy hacky...
        self.usage_data.electricity_usage = sorted(self.usage_data._uniq_electricity, key=lambda i: i.interval_start)
        self.usage_data.gas_usage = sorted(self.usage_data._uniq_gas, key=lambda i: i.interval_start)

        bytes_written = self.cache_path.write_text(self.json(exclude={"cache_path"}))
        LOG.info(
            f"Wrote {bytes_written} bytes to disk, "
            f"({len(self.usage_data.electricity_usage)} electricity & "
            f"{len(self.usage_data.gas_usage)} gas records).",
        )

    def earliest_reading(self, energy_type: EnergyType) -> RawUsage:
        match energy_type:
            case EnergyType.ELECTRICITY:
                return min(self.usage_data._uniq_electricity, key=lambda i: i.interval_start)
            case EnergyType.GAS:
                return min(self.usage_data._uniq_gas, key=lambda i: i.interval_start)

    def latest_reading(self, energy_type: EnergyType) -> RawUsage:
        match energy_type:
            case EnergyType.ELECTRICITY:
                return max(self.usage_data._uniq_electricity, key=lambda i: i.interval_end)
            case EnergyType.GAS:
                return max(self.usage_data._uniq_gas, key=lambda i: i.interval_end)

    def add_reading(self, readings: t.Iterable[RawUsage], energy_type: EnergyType) -> int:
        match energy_type:
            case EnergyType.ELECTRICITY:
                before = len(self.usage_data._uniq_electricity)
                self.usage_data._uniq_electricity.update(readings)
                after = len(self.usage_data._uniq_electricity)
                LOG.debug(f"Added {after-before} electricity records to cache.")
                return after - before

            case EnergyType.GAS:
                before = len(self.usage_data._uniq_gas)
                self.usage_data._uniq_gas.update(readings)
                after = len(self.usage_data._uniq_gas)
                LOG.debug(f"Added {after-before} gas records to cache.")
                return after - before

    def __enter__(self) -> "FileCache":
        """Provide context manager to flush on exit."""
        return self

    def __exit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional[TracebackType],
    ) -> t.Literal[False]:
        """Flush to disk on exit."""
        LOG.info("Flushing consumption data to disk.")
        self.flush()

        return False  # Don't suppress any exceptions
