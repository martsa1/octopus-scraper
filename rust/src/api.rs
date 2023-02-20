const URL_BASE: &str = "https://api.octopus.energy";
use anyhow::Result;
use serde::Deserialize;

pub struct Account {
    pub account_number: String,
    api_secret: String,
}

impl Account {
    pub fn new(account_number: String, api_secret: String) -> Account {
        Account {
            account_number,
            api_secret,
        }
    }
}

#[derive(Deserialize)]
struct MeterReading {
    interval_start: std::time::Duration,
    consumption: f32,
}

use std::path::PathBuf;

pub fn get_data_from_file(path: PathBuf) -> Result<Vec<MeterReading>> {
    serde_json::from_file();

    Err(anyhow::anyhow!("Failed to load data from disk."))
}


pub fn get_usage(account: &Account) -> Result<()> {
    println!("{}", URL_BASE);
    Ok(())
}
