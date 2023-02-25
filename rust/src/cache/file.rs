use super::DataCache;
use crate::types::usage::{EnergyType, MeterReading};
use anyhow::anyhow;
use log::{debug, error, info};

use serde::Deserialize;

#[derive(Debug, Deserialize, Default)]
struct UsageData {
    electricity_records: Vec<MeterReading>,
    gas_records: Vec<MeterReading>,
}

#[derive(Debug)]
struct FileCache {
    cache_path: std::path::PathBuf,
    readings: UsageData,
}

impl FileCache {
    fn new(cache_path: &std::path::Path) -> Self {
        FileCache {
            cache_path: cache_path.to_owned(),
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
        if !self.cache_path.exists() {
            std::fs::File::create(&self.cache_path)?;
        }

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
    fn load_data_cache_creates_new_file() -> anyhow::Result<()> {
        with_logs();

        let temp_path = TempDir::new(true);
        let cache_path = temp_path.temp_path.join("file_cache");
        info!("Using '{}' as temp path.", cache_path.display());

        let mut file_cache = FileCache::new(&cache_path);
        let load_result = file_cache.load();
        match load_result {
            Err(e) => {
                error!("Error loading data: {}", e);
                return Err(e);
            }
            _ => {}
        }
        assert!(!load_result.is_err());
        assert!(&cache_path.exists());

        Ok(())
    }

    #[test]
    fn load_sample_data_works_correctly() -> anyhow::Result<()> {
        with_logs();

        let temp_path = TempDir::new(true);
        let cache_path = temp_path.temp_path.join("file_cache");
        info!("Using '{}' as temp path.", cache_path.display());

        let sample_str = r#"
            {
                "electricity_records": [
                    {
                        "consumption": 1.0,
                        "interval_start": "2022-06-01T08:38:05+01:00",
                        "interval_end": "2022-06-01T09:08:05+01:00"
                    }
                ],
                "gas_records": [
                    {
                        "consumption": 1.0,
                        "interval_start": "2022-06-01T08:38:05+01:00",
                        "interval_end": "2022-06-01T09:08:05+01:00"
                    }
                ]
            }
        "#;
        let write_res = std::fs::write(&cache_path, sample_str);
        assert!(!write_res.is_err());
        debug!("Wrote sameple data to cache file: {}", cache_path.display());

        assert!(cache_path.exists());
        let cache_meta = std::fs::metadata(&cache_path)?;
        debug!(
            "metadata.len for '{}': {}",
            cache_path.display(),
            cache_meta.len()
        );
        assert!(cache_meta.len() as u64 == sample_str.len() as u64);

        let mut file_cache = FileCache::new(&cache_path);
        let load_res = file_cache.load();
        assert!(!load_res.is_err());
        debug!("Loaded file cache data from cache path");

        debug!("file_cache: {:#?}", file_cache);
        assert!(file_cache.readings.electricity_records.len() == 1);
        assert!(file_cache.readings.gas_records.len() == 1);

        assert!(file_cache.readings.electricity_records[0].consumption == 1.0);
        assert!(file_cache.readings.gas_records[0].consumption == 1.0);
        Ok(())
    }
}
