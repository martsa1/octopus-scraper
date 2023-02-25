use crate::types::usage::{EnergyType, MeterReading};
use anyhow::anyhow;
use log::{debug, error, info};

use serde::Deserialize;

#[derive(Deserialize, Default)]
struct UsageData {
    electricity_records: Vec<MeterReading>,
    gas_records: Vec<MeterReading>,
}

struct FileCache {
    cache_path: std::path::PathBuf,
    readings: UsageData,
}

trait DataCache {
    fn load(&mut self) -> anyhow::Result<()>;

    fn flush(&mut self) -> anyhow::Result<()>;

    fn most_recent_reading(&self, type_: EnergyType) -> anyhow::Result<MeterReading>;
}

impl FileCache {
    fn new(cache_path: std::path::PathBuf) -> Self {
        FileCache {
            cache_path: cache_path,
            readings: UsageData::default(),
        }
    }

    fn ensure_cache_path(&self) -> anyhow::Result<()> {
        match self.cache_path.parent() {
            Some(p) => {
                debug!(
                    "Created parent directories for '{}'",
                    self.cache_path.file_name().unwrap().to_str().unwrap()
                );
                std::fs::create_dir_all(p)?;
            }
            None => {
                return Err(anyhow!(
                    "Invalid cache_path parent directory: '{}'",
                    self.cache_path.display(),
                ))
            }
        }
        std::fs::File::create(&self.cache_path)?;

        Ok(())
    }
}

impl DataCache for FileCache {
    fn load(&mut self) -> anyhow::Result<()> {
        self.ensure_cache_path()?;

        debug!(
            "loading meter reading data from '{}'",
            self.cache_path.display()
        );
        // Grab a file handle for the cache path
        let file = std::fs::File::open(&self.cache_path)?;
        let f_reader = std::io::BufReader::new(file);

        debug!("Opened buffer to cache path");

        // Deserialise usage data from the file
        match serde_json::from_reader(f_reader) {
            Ok(data) => {
                self.readings = data;
                debug!(
                    "Loaded {} meter readings from cache file.",
                    self.readings.gas_records.len() + self.readings.electricity_records.len()
                );
            }
            Err(e) => match e.classify() {
                serde_json::error::Category::Eof => {
                    info!("No data in cache yet.");
                    self.readings = UsageData::default();
                }
                _ => {
                    error!("Failed to load data from cache: {}", e);
                    return Err(anyhow::format_err!(e));
                }
            },
        }

        Ok(())
    }

    fn flush(&mut self) -> anyhow::Result<()> {
        unimplemented!();
    }

    fn most_recent_reading(&self, _type_: EnergyType) -> anyhow::Result<MeterReading> {
        unimplemented!();
    }
}
#[cfg(test)]
mod test {
    use super::*;
    use crate::types::temp_dir::TempDir;

    fn with_logs() {
        let _ = env_logger::builder()
            .is_test(true)
            .filter_level(log::LevelFilter::Debug)
            .try_init();
    }

    #[test]
    fn load_data_cache_fails_for_missing_path() -> anyhow::Result<()> {
        with_logs();

        let temp_path = TempDir::new();
        let cache_path = temp_path.temp_path.join("file_cache");
        info!("Using '{}' as temp path.", cache_path.display());

        let mut file_cache = FileCache::new(cache_path);
        let load_result = file_cache.load();
        match load_result {
            Err(e) => {
                error!("Error loading data: {}", e);
                return Err(e);
            }
            _ => {}
        }
        assert!(!load_result.is_err());
        //assert!(load_result == ());

        Ok(())
    }
}
