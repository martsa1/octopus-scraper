use serde::Deserialize;

#[derive(Debug)]
pub enum EnergyType {
    Electricity,
    Gas,
}

/// Raw Meter reading type as used by octopus API.
#[derive(Debug, Deserialize)]
pub struct MeterReading {
    pub consumption: f32,
    pub interval_end: chrono::DateTime<chrono::Utc>,
    pub interval_start: chrono::DateTime<chrono::Utc>,
}

#[derive(Deserialize)]
pub struct RawUsageData {
  count: i32,
  next: Option<String>,
  previous: Option<String>,
  results: Vec<MeterReading>,
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_deserialise_meter_reading() {
        use chrono::{FixedOffset, TimeZone};
        // chrono::TimeZone provides the 'with_ymd_and_hms' method on various structs.

        let sample = r#"
            {
                "count": 1,
                "next": null,
                "previous": "https://no-such-luck",
                "results": [
                    {
                        "consumption": 0,
                        "interval_start": "2022-06-01T08:38:05+01:00",
                        "interval_end": "2022-06-01T09:08:05+01:00"
                    }
                ]
            }
        "#;
        let json_data = serde_json::from_str::<RawUsageData>(sample).unwrap();

        let hour = 3600;
        let expected_start = FixedOffset::east_opt(1 * hour)
            .unwrap()
            .with_ymd_and_hms(2022, 6, 1, 8, 38, 5)
            .unwrap();
        let expected_end = FixedOffset::east_opt(1 * hour)
            .unwrap()
            .with_ymd_and_hms(2022, 6, 1, 9, 8, 5)
            .unwrap();

        assert_eq!(json_data.count, 1);
        assert_eq!(json_data.next, None);
        assert_eq!(json_data.previous, Some("https://no-such-luck".to_owned()));
        assert_eq!(json_data.results.len(), 1);
        assert_eq!(json_data.results[0].consumption, 0 as f32);
        assert_eq!(json_data.results[0].interval_start, expected_start);
        assert_eq!(json_data.results[0].interval_end, expected_end);
    }
}
