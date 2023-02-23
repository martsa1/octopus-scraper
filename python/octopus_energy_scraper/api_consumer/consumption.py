"""Utilities used to retrieve consumption data from Octopus."""

import enum
import json
from time import sleep
import logging
import typing as t
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel, Field  # pylint: disable = no-name-in-module

from ..config import Settings
from ..types.usage import ConsumptionAPIData, EnergyType, RawUsage
from .client import octopus_client

LOG = logging.getLogger(__name__)


class OrderBy(enum.Enum):
    FORWARD = "period"
    BACKWARD = "-period"

    def __str__(self) -> str:
        return self.value


class ConsumptionOpts(BaseModel):
    period_from: t.Optional[datetime] = None
    period_to: t.Optional[datetime] = None
    page_size: t.Optional[int] = None
    page_num: t.Optional[int] = Field(None, alias="page")
    order_by: t.Optional[OrderBy] = None


def electric_usage(
    settings: Settings,
    consumption_options: ConsumptionOpts,
    client: t.Optional[httpx.Client] = None,
) -> httpx.Response:
    """Retrieve electricity consumption for the provided meter identifiers."""
    url_frag = (
        f"/electricity-meter-points/{settings.electricity_mpan}/meters/"
        f"{settings.electricity_serial}/consumption/"
    )
    query_params = json.loads(consumption_options.json(by_alias=True, exclude_none=True))
    LOG.debug(
        f"Retrieving Electicity consumption for meter: '{settings.electricity_mpan}:"
        f"{settings.electricity_serial}', params: {query_params}",
    )
    if client is None:
        with octopus_client(settings.api_key) as client:
            result = client.get(url_frag, params=query_params)
    else:
        result = client.get(url_frag, params=query_params)

    return result


def gas_usage(
    settings: Settings,
    consumption_options: ConsumptionOpts,
    client: t.Optional[httpx.Client] = None,
) -> httpx.Response:
    """Retrieve gas consumption for the provided meter identifiers."""
    url_frag = f"/gas-meter-points/{settings.gas_mprn}/meters/{settings.gas_serial}/consumption/"
    query_params = json.loads(consumption_options.json(by_alias=True, exclude_none=True))
    LOG.debug(
        f"Retrieving Gas consumption for meter: '{settings.gas_mprn}:{settings.gas_serial}'"
        f", params: {query_params}",
    )
    if client is None:
        with octopus_client(settings.api_key) as client:
            result = client.get(url_frag, params=query_params)
    else:
        result = client.get(url_frag, params=query_params)

    return result


def iter_consumption_readings(
    settings: Settings,
    query_opts: ConsumptionOpts,
    energy_type: EnergyType,
) -> t.Iterator[RawUsage]:
    """Iterate through electricity or gas readings.

    Selected Electricity or Gas readings using `energy_type`.

    Readings will observer ConsumptionOpts, iterating forward or backwards within the data
    requested from the UI, following pagination as needed.
    """
    min_api_call_interval = timedelta(seconds=0.5)
    next_call_cooldown = datetime.now()
    query_params = query_opts.copy()
    match energy_type:
        case EnergyType.ELECTRICITY:
            data_func = electric_usage
        case EnergyType.GAS:
            data_func = gas_usage

    if query_params.page_num is None:
        query_params.page_num = 1

    with octopus_client(settings.api_key) as client:
        while True:
            LOG.debug(
                f"Retrieving data from Octopus for {str(energy_type)}, options: {query_params}"
            )

            # Rate limit at least a bit...
            while datetime.now() < next_call_cooldown:
                sleep(min_api_call_interval.total_seconds() / 10)

            http_res = data_func(settings, query_params, client)
            next_call_cooldown = datetime.now() + min_api_call_interval

            http_res.raise_for_status()

            parse_start = datetime.utcnow()
            data = ConsumptionAPIData.parse_obj(http_res.json())
            parse_end = datetime.utcnow()
            LOG.debug(f"Deserialising API response took '{parse_end - parse_start}'")
            if query_params.page_num == 1:
                LOG.info(f"total records for {str(energy_type)}: {data.count}")

            LOG.debug(
                f"Retrieved {len(data.results)} records, most recent: "
                f"{max(data.results, key=lambda i: i.interval_end).interval_end.isoformat()}",
            )

            if query_params.page_size is None:
                query_params.page_size = len(data.results)

            for record in data.results:
                yield record

            if data.next_ is None:
                LOG.debug("No more records to fetch.")
                break

            query_params.page_num += 1
            LOG.info(
                f"Fetching next page of consumption data ({query_params.page_num} of "
                f"{data.count // query_params.page_size}) for {str(energy_type)}",
            )
