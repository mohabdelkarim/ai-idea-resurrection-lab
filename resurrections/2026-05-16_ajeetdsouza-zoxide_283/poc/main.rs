use std::collections::HashMap;
use std::error::Error;
use std::path::{Path, PathBuf};
use std::fs;
use tokio;
use tokio::fs::OpenOptions;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use anyhow::{Context, Result};
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
struct Entry {
    path: PathBuf,
    score: u32,
}

pub struct Database {
    path: PathBuf,
}

impl Database {
    pub async fn new(path: PathBuf) -> Result<Self> {
        Ok(Database { path })
    }

    pub async fn get(&self, query: &str) -> Result<Vec<Entry>> {
        let mut file = OpenOptions::new()
            .read(true)
            .open(&self.path)
            .await
            .context("Failed to open database")?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)
            .await
            .context("Failed to read database")?;
        let entries: Vec<Entry> = serde_json::from_str(&contents)
            .context("Failed to parse database")?;
        let query = query.to_lowercase();
        Ok(entries
            .into_iter()
            .filter(|entry| entry.path.to_str().unwrap().to_lowercase().contains(&query))
            .collect())
    }

    pub async fn add(&self, entry: Entry) -> Result<()> {
        let mut file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(&self.path)
            .await
            .context("Failed to open database")?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)
            .await
            .context("Failed to read database")?;
        let mut entries: Vec<Entry> = if contents.is_empty() {
            Vec::new()
        } else {
            serde_json::from_str(&contents)
                .context("Failed to parse database")?
        };
        entries.push(entry);
        file.set_len(0)
            .await
            .context("Failed to truncate database")?;
        file.write_all(serde_json::to_string_pretty(&entries)?.as_bytes())
            .await
            .context("Failed to write database")?;
        Ok(())
    }
}

pub struct Zoxide {
    database: Database,
}

impl Zoxide {
    pub async fn new(database_path: PathBuf) -> Result<Self> {
        let database = Database::new(database_path).await?;
        Ok(Zoxide { database })
    }

    pub async fn query(&self, query: &str) -> Result<Vec<Entry>> {
        self.database.get(query).await
    }

    pub async fn add(&self, path: PathBuf) -> Result<()> {
        let entry = Entry { path, score: 1 };
        self.database.add(entry).await
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let database_path = Path::new("zoxide.db").to_path_buf();
    let zoxide = Zoxide::new(database_path).await?;
    zoxide.add(Path::new("/home/user/").to_path_buf()).await?;
    let results = zoxide.query("home").await?;
    for entry in results {
        println!("{:?}", entry.path);
    }
    Ok(())
}