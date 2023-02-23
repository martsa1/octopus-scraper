"""Verify basic file cache behaviour."""

import json
import logging
import typing as t
from datetime import datetime
from pathlib import Path

import hypothesis as h
from _pytest.tmpdir import TempPathFactory
from hypothesis import strategies as st

from octopus_energy_scraper.data_cache.file import FileCache
from octopus_energy_scraper.types.usage import RawUsage, EnergyType

# def mk_reading(consumption: float, start: dt.datetime, end: dt.datetime) -> t.Mapping[str, t.Any]:
#     if consumption < 0:
#         raise ValueError()
#     return {"consumption": consumption, "interval_start": start, "interval_end": end}

LOG = logging.getLogger(__name__)


def tmp_path_per_case(tmp_path_factory: TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("file-cache-test-")


GasReadingsStrat = st.lists(
    st.builds(
        RawUsage,
        consumption=st.floats(min_value=0),
        interval_start=st.datetimes(
            min_value=datetime(2014, 1, 1),
            max_value=datetime.now(),
            timezones=st.timezones(),
            allow_imaginary=False,
        ),
        interval_end=st.datetimes(
            min_value=datetime(2014, 1, 1),
            max_value=datetime.now(),
            timezones=st.timezones(),
            allow_imaginary=False,
        ),
    ),
    max_size=10,
)

ElectricityReadingsStrat = st.lists(
    st.builds(
        RawUsage,
        consumption=st.floats(min_value=0),
        interval_start=st.datetimes(
            min_value=datetime(2014, 1, 1),
            max_value=datetime.now(),
            timezones=st.timezones(),
            allow_imaginary=False,
        ),
        interval_end=st.datetimes(
            min_value=datetime(2014, 1, 1),
            max_value=datetime.now(),
            timezones=st.timezones(),
            allow_imaginary=False,
        ),
    ),
    max_size=10,
)


@h.given(electric_readings=ElectricityReadingsStrat, gas_readings=GasReadingsStrat)
def test_flush_and_load_data_consistent(
    electric_readings: t.MutableSequence[RawUsage],
    gas_readings: t.MutableSequence[RawUsage],
    tmp_path_factory: TempPathFactory,
) -> None:
    base_dir = tmp_path_per_case(tmp_path_factory)
    cache_path = base_dir / "cache.json"
    LOG.info("Cache path is '%s'", str(cache_path))
    sample = FileCache(cache_path=cache_path)

    sample.add_reading(electric_readings, EnergyType.ELECTRICITY)
    sample.add_reading(gas_readings, EnergyType.GAS)

    sample.flush()

    # Ensure it serialises to disk
    assert json.loads(cache_path.read_text())
    LOG.debug("sample: %s", sample)

    loaded_sample = FileCache(cache_path=cache_path)
    loaded_sample.load()
    LOG.debug("loaded_sample: %s", loaded_sample)

    assert loaded_sample == sample
