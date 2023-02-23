"""Logic that fetches data from Octopus and stores it using a storage cache."""

import logging
import typing as t
from datetime import datetime
from collections import defaultdict

from .api_consumer.consumption import (
    ConsumptionOpts,
    OrderBy,
    iter_consumption_readings,
)
from .config import Settings
from .data_cache.base import CacheBase
from .types.usage import EnergyType


LOG = logging.getLogger(__name__)


class Scraper:

    def __init__(
        self,
        settings: Settings,
        storage: CacheBase,
    ) -> None:
        self.settings = settings
        self.storage = storage

        self.gas_records = 0
        self.electricity_records = 0

        self.earliest_record: t.Optional[datetime] = None

    def sync_data(
        self,
        start_date: t.Optional[datetime] = None,
        batch_size: int = 1000,
    ) -> t.Mapping[EnergyType, int]:
        """Retrieve data from octopus and flush to data store.

        Returns number of records retrieved.
        """
        query_opts = ConsumptionOpts(
            order_by=OrderBy.FORWARD,
            page_num=1,
            page_size=batch_size,
            period_from=start_date,
        )

        # Seems a little shit that the type-annotations for defaultdict expect a str key.
        records_added: t.MutableMapping[EnergyType, int] = t.cast(
            t.DefaultDict[EnergyType, int],
            defaultdict(int),
        )

        for type_ in EnergyType:
            # Cache data in memory and flush to disk on exit from the context manager
            with self.storage:
                LOG.info(f"Retrieving consumption data for {str(type_)}")
                readings = set(iter_consumption_readings(self.settings, query_opts, type_))
                records_added[type_] += len(readings)
                self.storage.add_reading(readings, type_)

        LOG.debug(f"Retrieved records: {records_added}")
        return records_added
