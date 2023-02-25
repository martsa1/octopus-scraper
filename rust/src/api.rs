use super::types::usage::MeterReading;
use anyhow::Result;

const URL_BASE: &str = "https://api.octopus.energy";

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

use std::path::PathBuf;

pub fn get_data_from_file(path: PathBuf) -> Result<Vec<MeterReading>> {
    let _json_data = serde_json::from_str::<MeterReading>(&std::fs::read_to_string(path)?);

    Err(anyhow::anyhow!("Failed to load data from disk."))
}

pub fn get_usage(account: &Account) -> Result<()> {
    println!("{}", URL_BASE);
    Ok(())
}
