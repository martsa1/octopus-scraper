mod api;
mod args;
mod cache;
mod types;
use clap::Parser;
use log::debug;

fn main() -> anyhow::Result<()> {
    env_logger::init();

    let args = args::Cli::parse();
    //let account = crate::api::Account::new(args.account_number, args.api_key);
    //api::get_usage(&account)
    let client = reqwest::blocking::Client::new();
    let electricity_req = api::electricity_usage(
        &client,
        &args.api_key,
        &args.electricity_id,
        &args.electricity_serial,
    )?.send();
    debug!("Response: {:#?}", electricity_req);
    Ok(())
}
