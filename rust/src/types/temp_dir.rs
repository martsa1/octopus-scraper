use std::path;
use log::{debug, error};

#[derive(Default, Debug)]
pub struct TempDir {
    pub temp_path: path::PathBuf,
}

impl TempDir {
    pub fn new() -> Self {
        use uuid::Uuid;
         let mut temp = Self::default();
         let rand_dir_name = Uuid::new_v4().hyphenated().to_string();
         temp.temp_path = std::env::temp_dir().join(rand_dir_name);
         std::fs::create_dir_all(&temp.temp_path).unwrap();
         debug!("Created temp dir at {}", temp.temp_path.display());

         temp
    }
}
impl Drop for TempDir {
    fn drop(&mut self) {
        debug!("Dropping temp path");
        if self.temp_path.exists() {
            debug!("{} exists, so removing it and all its contents", self.temp_path.display());
            match std::fs::remove_dir_all(&self.temp_path) {
                Err(e) => {
                    error!("Failed to remove directory: {}", e);
                }
                _ => {}
            }
        }
    }
}

