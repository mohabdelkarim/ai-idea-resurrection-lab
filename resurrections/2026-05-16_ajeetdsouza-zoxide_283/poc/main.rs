//! Proof of concept: expose zoxide as a Rust library crate
//!
//! Demonstrates the proposed public library API surface WITHOUT using any
//! internal or non-pub zoxide types. Uses ONLY the Rust standard library —
//! no external crates required to run this PoC.
//!
//! The issue asks for zoxide to be usable as a library crate so that tools
//! like fzf integrations, IDE plugins, and shell completers can query the
//! frecency database programmatically.
//!
//! Run:
//!   rustc main.rs -o zoxide_lib_poc && ./zoxide_lib_poc [query]
//!
//! Or with cargo:
//!   cargo init --name zoxide_lib_poc
//!   cp main.rs src/main.rs
//!   cargo run -- home

use std::collections::HashMap;
use std::env;
use std::fs;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

// ---------------------------------------------------------------------------
// Frecency score — mirrors zoxide's internal algorithm.
// Score = sum of weights, where each visit within a time window contributes
// a weight that decays with age. This is the same logic zoxide uses.
// ---------------------------------------------------------------------------

const HOUR: u64 = 3600;
const DAY: u64 = 86400;
const WEEK: u64 = 604800;

fn frecency_score(accesses: &[u64], now: u64) -> f64 {
    let mut score = 0.0f64;
    for &timestamp in accesses {
        let age = now.saturating_sub(timestamp);
        let weight = if age < HOUR {
            4.0
        } else if age < DAY {
            2.0
        } else if age < WEEK {
            1.0
        } else {
            0.5
        };
        score += weight;
    }
    score
}

// ---------------------------------------------------------------------------
// Database — a minimal in-memory representation of what the proposed
// `zoxide::Database` public struct would expose.
// ---------------------------------------------------------------------------

/// A single directory entry in the frecency database.
#[derive(Debug, Clone)]
pub struct Dir {
    /// Absolute path of the directory.
    pub path: PathBuf,
    /// Unix timestamps (seconds) of each recorded visit.
    pub accesses: Vec<u64>,
}

impl Dir {
    /// Compute the frecency score at the given time.
    pub fn score(&self, now: u64) -> f64 {
        frecency_score(&self.accesses, now)
    }

    /// Number of times this directory has been visited.
    pub fn visit_count(&self) -> usize {
        self.accesses.len()
    }
}

/// The proposed public `zoxide::Database` type.
/// In the real implementation this would wrap the internal sled-based store;
/// here we use a plain HashMap over a TSV file (same on-disk format zoxide uses
/// before the sled migration, and still used by `zoxide export`).
pub struct Database {
    entries: HashMap<PathBuf, Dir>,
}

impl Database {
    /// Open the database at `path`.
    /// Accepts the path to the zoxide TSV export (`zoxide import --from=z`).
    /// Returns an empty database if the file does not exist.
    pub fn open(path: &Path) -> io::Result<Self> {
        let mut entries: HashMap<PathBuf, Dir> = HashMap::new();

        let file = match fs::File::open(path) {
            Ok(f) => f,
            Err(ref e) if e.kind() == io::ErrorKind::NotFound => {
                // Fresh install — empty DB is valid
                return Ok(Database { entries });
            }
            Err(e) => return Err(e),
        };

        for line in io::BufReader::new(file).lines() {
            let line = line?;
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            // TSV format: <rank>\t<timestamp>\t<path>
            let cols: Vec<&str> = line.splitn(3, '\t').collect();
            if cols.len() < 3 {
                continue;
            }
            let timestamp: u64 = cols[1].parse().unwrap_or(0);
            let dir_path = PathBuf::from(cols[2]);
            entries
                .entry(dir_path.clone())
                .or_insert_with(|| Dir { path: dir_path, accesses: Vec::new() })
                .accesses
                .push(timestamp);
        }

        Ok(Database { entries })
    }

    /// Record a visit to `path` at time `now`.
    pub fn add(&mut self, path: &Path, now: u64) {
        let entry = self
            .entries
            .entry(path.to_path_buf())
            .or_insert_with(|| Dir { path: path.to_path_buf(), accesses: Vec::new() });
        entry.accesses.push(now);
    }

    /// Query directories whose path contains ALL keywords (case-insensitive),
    /// sorted by descending frecency score.
    pub fn query(&self, keywords: &[&str], now: u64) -> Vec<&Dir> {
        let keywords_lower: Vec<String> =
            keywords.iter().map(|k| k.to_lowercase()).collect();

        let mut results: Vec<&Dir> = self
            .entries
            .values()
            .filter(|dir| {
                let path_str = dir.path.to_string_lossy().to_lowercase();
                keywords_lower.iter().all(|kw| path_str.contains(kw.as_str()))
            })
            .collect();

        results.sort_by(|a, b| {
            b.score(now)
                .partial_cmp(&a.score(now))
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        results
    }

    /// Return all entries sorted by descending frecency score.
    pub fn all_sorted(&self, now: u64) -> Vec<&Dir> {
        self.query(&[], now)
    }

    /// Total number of directory entries.
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
}

// ---------------------------------------------------------------------------
// Resolve the database path using the same env-var logic as zoxide itself.
// ---------------------------------------------------------------------------

fn resolve_db_path() -> PathBuf {
    if let Ok(p) = env::var("_ZO_DATA_DIR") {
        return PathBuf::from(p).join("db.zo");
    }
    if let Ok(xdg) = env::var("XDG_DATA_HOME") {
        return PathBuf::from(xdg).join("zoxide").join("db.zo");
    }
    // Platform default — no external `dirs` crate needed
    #[cfg(unix)]
    {
        if let Ok(home) = env::var("HOME") {
            return PathBuf::from(home).join(".local").join("share").join("zoxide").join("db.zo");
        }
    }
    #[cfg(windows)]
    {
        if let Ok(appdata) = env::var("LOCALAPPDATA") {
            return PathBuf::from(appdata).join("zoxide").join("db.zo");
        }
    }
    PathBuf::from("db.zo")
}

fn current_time() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

// ---------------------------------------------------------------------------
// Demo main
// ---------------------------------------------------------------------------

fn main() {
    let db_path = resolve_db_path();
    let query: String = env::args().skip(1).collect::<Vec<_>>().join(" ");
    let keywords: Vec<&str> = if query.is_empty() {
        vec![]
    } else {
        query.split_whitespace().collect()
    };

    println!("zoxide library PoC");
    println!("DB path : {}", db_path.display());
    println!("Query   : {:?}", keywords);
    println!();

    let db = match Database::open(&db_path) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("Error opening database: {}", e);
            eprintln!("Run `z` a few times first to populate the database.");
            std::process::exit(1);
        }
    };

    if db.is_empty() {
        println!("Database is empty. Run `z some/directory` to start tracking.");
        return;
    }

    let now = current_time();
    let results = db.query(&keywords, now);

    if results.is_empty() {
        println!("No results for {:?}.", keywords);
        return;
    }

    println!("{:<10} {:<6} {}", "SCORE", "VISITS", "PATH");
    println!("{}", "-".repeat(60));
    for dir in results.iter().take(20) {
        println!(
            "{:<10.2} {:<6} {}",
            dir.score(now),
            dir.visit_count(),
            dir.path.display()
        );
    }
}
