use super::types::usage::MeterReading;
use anyhow::Result;
use log::debug;
use reqwest::blocking::Client;
use reqwest::blocking::RequestBuilder;
use serde::Serialize;

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

#[derive(Serialize, Debug, Default)]
struct QueryParams {
    /// Show consumption from the given datetime (inclusive). This parameter can be provided on
    /// its own.
    period_from: Option<chrono::DateTime<chrono::Utc>>,

    /// Show consumption to the given datetime (exclusive). This parameter also requires providing
    /// the period_from parameter to create a range.
    period_to: Option<chrono::DateTime<chrono::Utc>>,

    /// Page size of returned results. Default is 100, maximum is 25,000 to give a full year of
    /// half-hourly consumption details.
    page_size: Option<u32>,

    /// Ordering of results returned. Default is that results are returned in reverse order from
    /// latest available figure. Valid values: * ‘period’, to give results ordered forward. *
    /// ‘-period’, (default), to give results ordered from most recent backwards.
    order_by: Option<String>,

    /// Aggregates consumption over a specified time period. A day is considered to start and end
    /// at midnight in the server’s timezone. The default is that consumption is returned in
    /// half-hour periods. Accepted values are: * ‘hour’ * ‘day’ * ‘week’ * ‘month’ * ‘quarter’
    group_by: Option<String>,
}

/// Prep an HTTP get request with authemtication etc. setup
fn octopus_request(
    api_secret: &str,
    url_frag: reqwest::Url,
    client: &Client,
) -> anyhow::Result<RequestBuilder> {
    let request_base = client.get(url_frag).basic_auth(api_secret, None::<&str>);

    Ok(request_base)
}

pub fn electricity_usage(
    client: &Client,
    api_secret: &str,
    electricity_id: &str,
    electricity_serial: &str,
) -> Result<RequestBuilder> {
    // N.B. .join will truncate if you provide a '/' prefix...
    let url = reqwest::Url::parse(URL_BASE)?
        .join("v1/electricity-meter-points/")?
        .join(&format!("{electricity_id}/"))?
        .join("meters/")?
        .join(&format!("{electricity_serial}/"))?
        .join("consumption/")?;

    let mut query_params = QueryParams::default();
    query_params.page_size = Some(3);

    let request = octopus_request(api_secret, url, &client)?
        .query(&query_params)
    ;

    debug!("Request for electricity usage:\n{:#?}", request);

    Ok(request)
}

pub fn gas_usage(
    client: &Client,
    api_secret: &str,
    gas_id: &str,
    gas_serial: &str,
) -> Result<RequestBuilder> {
    let url = reqwest::Url::parse(URL_BASE)?
        .join("v1/gas-meter-points/")?
        .join(&format!("{gas_id}/"))?
        .join("meters/")?
        .join(&format!("{gas_serial}/"))?
        .join("consumption/")?;

    let request = octopus_request(api_secret, url, client);
    debug!("Request for gas usage:\n{:#?}", request);

    request
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::util::with_logs;

    #[test]
    fn print_electricity_request() -> Result<()> {
        with_logs();

        let client = Client::new();
        let api_secret = "foobar";
        let electricity_id = "elec1234";
        let electricity_serial = "4321cele";

        let request = electricity_usage(&client, api_secret, electricity_id, electricity_serial);
        assert!(!request.is_err());

        let request = request?;
        let response = request.send();

        debug!("Response: {:#?}", response);

        assert!(false);
        Ok(())
    }
}
