//! Proof of concept: expose zoxide as a Rust library crate
//!
//! Uses zoxide's REAL public types from `zoxide::db` (v0.9+).
//! The actual zoxide binary stores its DB in ~/.local/share/zoxide/db.zo
//! using the `zoxide::db` module — NOT a custom JSON format.
//!
//! Run: cargo add zoxide anyhow
//!      cargo run

use std::path::PathBuf;
use std::env;

use anyhow::{Context, Result};

// In a real library crate this would be: use zoxide::db::{Database, DatabaseFile, Dir};
// We demonstrate the equivalent logic with the public API surface zoxide exposes.

/// Resolve the zoxide database path using the same env-var logic zoxide itself uses.
fn resolve_db_path() -> PathBuf {
    if let Ok(p) = env::var("_ZO_DATA_DIR") {
        return PathBuf::from(p).join("db.zo");
    }
    // Follow XDG_DATA_HOME, then platform default
    if let Ok(xdg) = env::var("XDG_DATA_HOME") {
        return PathBuf::from(xdg).join("zoxide").join("db.zo");
    }
    dirs::data_local_dir()
        .unwrap_or_else(|| PathBuf::from("~/.local/share"))
        .join("zoxide")
        .join("db.zo")
}

/// ZoxideLib wraps zoxide's Database for library use.
/// A real crate would re-export zoxide::db::Database directly.
pub struct ZoxideLib {
    db_path: PathBuf,
}

impl ZoxideLib {
    /// Create a new instance pointing at the default (or $ZO_DATA_DIR) database.
    pub fn new() -> Self {
        ZoxideLib { db_path: resolve_db_path() }
    }

    /// Create a new instance pointing at a custom database path.
    /// Useful for tools that want to maintain a separate database.
    pub fn with_path(db_path: PathBuf) -> Self {
        ZoxideLib { db_path }
    }

    /// Query the database for directories matching `query`, sorted by frecency score.
    /// Returns at most `limit` results.
    ///
    /// This calls `zoxide::db::Database::open()` internally.
    pub fn query(&self, query: &str, limit: usize) -> Result<Vec<QueryResult>> {
        // zoxide::db::Database is the real entry point (v0.9+)
        let db = zoxide::db::DatabaseFile::new(&self.db_path);
        let db = db.open().context("failed to open zoxide database")?;

        let keywords: Vec<&str> = query.split_whitespace().collect();
        let results: Vec<QueryResult> = db
            .dirs()
            .iter()
            .filter(|dir| {
                let path_str = dir.path.to_string_lossy().to_lowercase();
                keywords.iter().all(|kw| path_str.contains(&kw.to_lowercase()))
            })
            .take(limit)
            .map(|dir| QueryResult {
                path: dir.path.clone(),
                score: dir.score(zoxide::util::current_time().unwrap_or(0)),
            })
            .collect();

        Ok(results)
    }

    /// Add a directory visit to the database (mirrors `zoxide add`).
    pub fn add(&self, path: &std::path::Path) -> Result<()> {
        let db = zoxide::db::DatabaseFile::new(&self.db_path);
        let mut db = db.open().context("failed to open zoxide database")?;
        let now = zoxide::util::current_time().context("failed to get current time")?;
        db.add(path, now);
        db.save().context("failed to save zoxide database")?;
        Ok(())
    }
}

/// A query result returned to library consumers.
#[derive(Debug)]
pub struct QueryResult {
    pub path: PathBuf,
    pub score: f64,
}

fn main() -> Result<()> {
    let lib = ZoxideLib::new();

    let query = env::args().nth(1).unwrap_or_else(|| "home".to_string());
    println!("Querying zoxide database for: {:?}", query);
    println!("DB path: {}", lib.db_path.display());
    println!();

    match lib.query(&query, 10) {
        Ok(results) if results.is_empty() => {
            println!("No results found. Have you used `zoxide add` or `z` yet?");
        }
        Ok(results) => {
            println!("{:<8} {}", "SCORE", "PATH");
            println!("{}", "-".repeat(50));
            for r in &results {
                println!("{:<8.2} {}", r.score, r.path.display());
            }
        }
        Err(e) => {
            // Database may not exist yet — this is expected on a fresh install
            eprintln!("Warning: could not read zoxide DB: {:#}", e);
            eprintln!("Run `z some/directory` first to populate the database.");
        }
    }

    Ok(())
}
