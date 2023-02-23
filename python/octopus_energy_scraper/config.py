"""Pydantic powered config."""

from pydantic import BaseModel, BaseSettings, Field  # pylint: disable = no-name-in-module


class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")
    account_number: str
    electricity_mpan: str
    electricity_serial: str
    gas_mprn: str
    gas_serial: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
