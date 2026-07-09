use std::fs;
use std::path::Path;
use std::time::{Duration, SystemTime};
use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use regex::Regex;

#[derive(Parser)]
struct Cli {
    #[clap(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    Search {
        #[clap(short, long)]
        path: String,
        #[clap(short, long)]
        atime: Option<i32>,
        #[clap(short, long)]
        ctime: Option<i32>,
        #[clap(short, long)]
        mtime: Option<i32>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Some(Command::Search { path, atime, ctime, mtime }) => {
            search_files(&path, atime, ctime, mtime)?;
        }
        None => {
            println!("No command provided.");
        }
    }
    Ok(())
}

fn search_files(path: &str, atime: Option<i32>, ctime: Option<i32>, mtime: Option<i32>) -> Result<()> {
    let re = Regex::new("[^/"]+")?;
    for entry in fs::read_dir(path).context("Failed to read directory")? {
        let entry = entry.context("Failed to read directory entry")?;
        let file_name = entry.file_name().to_string_lossy();
        let file_path = entry.path();
        if file_path.is_file() {
            let metadata = fs::metadata(&file_path).context("Failed to get file metadata")?;
            let file_modified = metadata.modified().context("Failed to get file modified time")?;
            let file_accessed = metadata.accessed().context("Failed to get file accessed time")?;
            let file_created = metadata.created().context("Failed to get file created time")?;
            let mut matches = true;
            if let Some(atime) = atime {
                let duration = Duration::from_secs(atime as u64 * 24 * 60 * 60);
                let atime_sys = file_accessed.context("Failed to get file accessed time")?;
                let now = SystemTime::now();
                let elapsed = now.duration_since(atime_sys).unwrap_or(Duration::from_secs(0));
                if elapsed < duration {
                    matches = false;
                }
            }
            if let Some(ctime) = ctime {
                let duration = Duration::from_secs(ctime as u64 * 24 * 60 * 60);
                let ctime_sys = file_created.context("Failed to get file created time")?;
                let now = SystemTime::now();
                let elapsed = now.duration_since(ctime_sys).unwrap_or(Duration::from_secs(0));
                if elapsed < duration {
                    matches = false;
                }
            }
            if let Some(mtime) = mtime {
                let duration = Duration::from_secs(mtime as u64 * 24 * 60 * 60);
                let mtime_sys = file_modified.context("Failed to get file modified time")?;
                let now = SystemTime::now();
                let elapsed = now.duration_since(mtime_sys).unwrap_or(Duration::from_secs(0));
                if elapsed < duration {
                    matches = false;
                }
            }
            if matches {
                println!("{}", file_name);
            }
        }
    }
    Ok(())
}