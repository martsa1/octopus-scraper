"""Test base usage serialisation etc."""

import json
import typing as t
from datetime import datetime, timezone
from pathlib import Path

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from octopus_energy_scraper.types.usage import RawUsage


@pytest.fixture
def sample_electrical_data() -> t.Mapping[str, t.Any]:
    with Path(__file__).parent.joinpath("sample_electricity_usage.json").open("r") as file_:
        return json.load(file_)  # type: ignore[no-any-return]


@pytest.fixture
def sample_gas_data() -> t.Mapping[str, t.Any]:
    with Path(__file__).parent.joinpath("sample_gas_usage.json").open("r") as file_:
        return json.load(file_)  # type: ignore[no-any-return]


@given(st.builds(RawUsage))
@example(
    RawUsage(
        consumption=0,
        interval_start=datetime.now(timezone.utc).isoformat(),
        interval_end=datetime.now(timezone.utc).isoformat(),
    ),
)
def test_raw_usage(instance: RawUsage) -> None:
    assert instance.consumption >= 0


def test_deserialise(
    sample_gas_data: t.Mapping[str, t.Any],
    sample_electrical_data: t.Mapping[str, t.Any],
) -> None:
    gas_readings = RawUsage.from_raw_api_json(sample_gas_data)
    assert len(gas_readings) == 3
    assert all(isinstance(reading, RawUsage) for reading in gas_readings)

    electric_readings = RawUsage.from_raw_api_json(sample_electrical_data)
    assert len(electric_readings)
    assert all(isinstance(reading, RawUsage) for reading in electric_readings)


# Octopus was founded in 2015, so we'll never see dates earlier than that in consumption data.
@given(
    st.datetimes(
        min_value=datetime(2014, 1, 1),
        max_value=datetime.now(),
        timezones=st.timezones(),
    ),
)
def test_coerce_to_utc(in_: datetime) -> None:
    coerced = RawUsage._coerce_to_utc(in_)
    assert in_ == coerced
