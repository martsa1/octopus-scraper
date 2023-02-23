"""Base types for data storage."""

import typing as t
from types import TracebackType

from abc import ABC, abstractmethod

from ..types.usage import EnergyType, RawUsage


class CacheBase(ABC):
    """Storage API to persist consumption (and other) data retrieved from Octopus."""

    @abstractmethod
    def load(self) -> None:
        """Load stored data from cache."""

    @abstractmethod
    def flush(self) -> None:
        """Flush current data to cache."""

    @abstractmethod
    def earliest_reading(self, energy_type: EnergyType) -> t.Optional[RawUsage]:
        """Retrieve the earliest energy reading from cache."""

    @abstractmethod
    def latest_reading(self, energy_type: EnergyType) -> t.Optional[RawUsage]:
        """Retrieve the most recent energy reading from cache."""

    @abstractmethod
    def add_reading(self, reading: t.Iterable[RawUsage], energy_type: EnergyType) -> int:
        """Add new consumption readings to data store.

        Should return number of records added, false if it was already present.
        """

    @abstractmethod
    def __enter__(self) -> "CacheBase":
        """Provide context manager to provide transactions on IO etc."""

    @abstractmethod
    def __exit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional[TracebackType],
    ) -> bool:
        pass
