use clap::Parser;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
pub struct Cli {
    /// Account number for the user whose usage we wish to retrieve
    pub account_number: String,

    /// API Secret. Retrieve from "https://octopus.energy/dashboard/developer/"
    pub api_key: String,
}
