mod api;
mod args;
mod types;
mod cache;
use clap::Parser;

fn main() -> anyhow::Result<()> {
    env_logger::init();

    let args = args::Cli::parse();
    let account = crate::api::Account::new(args.account_number, args.api_key);
    api::get_usage(&account)
}

