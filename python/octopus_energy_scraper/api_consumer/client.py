import typing as t
from contextlib import contextmanager

import httpx


@contextmanager
def octopus_client(api_key: str, version: str = "v1") -> t.Iterator[httpx.Client]:
    yield httpx.Client(
        base_url=f"https://api.octopus.energy/{version}",
        auth=httpx.BasicAuth(username=api_key, password=""),
    )
