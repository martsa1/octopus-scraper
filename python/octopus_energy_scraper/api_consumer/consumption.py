"""Utilities used to retrieve consumption data from Octopus."""

import typing as t

from ..types.electricity import ElectricityUsage


BASE_URL = "https://api.octopus.energy"


def electric_usage(mpan: str, serial_number: str) -> t.Sequence[t.Any]:
    """Retrieve electricity consumption for the provided meter identifiers."""
    pass


def gas_usage(mprn: str, serial_number: str) -> t.Sequence[t.Any]:
    """Retrieve gas consumption for the provided meter identifiers"""
