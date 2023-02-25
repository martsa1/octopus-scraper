mod file;
use super::types::usage::{EnergyType, MeterReading};

trait DataCache {
    fn load(&mut self) -> anyhow::Result<()>;

    fn flush(&mut self) -> anyhow::Result<()>;

    fn most_recent_reading(&self, type_: EnergyType) -> anyhow::Result<MeterReading>;
}
