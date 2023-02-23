import logging
from pathlib import Path

from octopus_energy_scraper.config import Settings
from octopus_energy_scraper.data_cache.file import FileCache
from octopus_energy_scraper.scraper import Scraper
from octopus_energy_scraper.types.usage import EnergyType


def configure_logs() -> None:
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)


def main() -> None:
    configure_logs()
    log = logging.getLogger(__name__)
    settings = Settings()  # Parsed from environment or .env file etc.

    data_path = Path("./consumption_data.json").resolve()
    log.info(f"Syncing octopus data to file: {data_path.relative_to(Path('.').resolve())}.")

    file_cache = FileCache(cache_path=data_path)
    file_cache.load()
    scraper = Scraper(settings, file_cache)

    records_added = scraper.sync_data()

    log.info(
        f"Added {records_added[EnergyType.ELECTRICITY]} electricity records and "
        f"{records_added[EnergyType.GAS]} gas records.",
    )


if __name__ == "__main__":
    main()
