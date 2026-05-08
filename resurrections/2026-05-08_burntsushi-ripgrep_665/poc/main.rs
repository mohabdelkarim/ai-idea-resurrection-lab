use clap::Parser;
use regex::Regex;
use std::fs;
use std::path::PathBuf;
use url::Url;
use walkdir::WalkDir;

/// Proof-of-concept: ripgrep --file-url flag
/// Prints matched file paths as clickable file:// URLs instead of plain paths.
/// Works with terminals that support OSC 8 hyperlinks (Warp, Ghostty, iTerm2, VS Code).
#[derive(Parser, Debug)]
#[command(name = "rg-file-url", version = "0.1.0", about = "PoC: rg with --file-url support")]
struct Args {
    /// Search pattern (regex)
    pattern: String,

    /// Path to search in (file or directory)
    path: PathBuf,

    /// Print file paths as file:// URLs instead of plain paths
    #[arg(long)]
    file_url: bool,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let re = Regex::new(&args.pattern)?;

    // Canonicalize so file:// URLs are always absolute
    let search_root = fs::canonicalize(&args.path)?;

    for entry in WalkDir::new(&search_root)
        .follow_links(false)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
    {
        let file_path = entry.path();
        // Skip files that can't be read as UTF-8 (binary files)
        let Ok(content) = fs::read_to_string(file_path) else {
            continue;
        };

        for (line_idx, line) in content.lines().enumerate() {
            if re.is_match(line) {
                let line_number = line_idx + 1;
                if args.file_url {
                    // file:// URL — canonicalize guarantees absolute path
                    let url = Url::from_file_path(file_path)
                        .expect("canonicalized path must be absolute");
                    // Append line fragment for editor deep-linking (VS Code, Zed, etc.)
                    println!("{}#L{}:{}", url, line_number, line);
                } else {
                    println!("{}:{}:{}", file_path.display(), line_number, line);
                }
            }
        }
    }

    Ok(())
}
