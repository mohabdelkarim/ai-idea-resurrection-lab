use std::env;
use std::path::{Path, PathBuf};
use std::ffi::OsString;
use std::process;

/// Strategy for path remapping.
#[derive(Debug)]
enum RemapStrategy {
    /// Keep the path as‑is (no remapping).
    None,
    /// Remap absolute paths to a crate‑relative form.
    CrateRelative,
}

/// Configuration parsed from command line arguments.
#[derive(Debug)]
struct Config {
    /// The chosen remap strategy.
    strategy: RemapStrategy,
    /// The input file path to be remapped.
    input_path: PathBuf,
}

impl Config {
    /// Parse command line arguments into a Config.
    fn from_args<I, T>(mut args: I) -> Result<Self, String>
    where
        I: Iterator<Item = T>,
        T: Into<OsString>,
    {
        // Skip program name.
        args.next();
        let mut strategy = RemapStrategy::None;
        let mut input_path: Option<PathBuf> = None;
        while let Some(arg_os) = args.next() {
            let arg = arg_os.into();
            let arg_str = arg.to_string_lossy();
            if arg_str.starts_with("--remap-path-prefix") {
                // Accept forms: --remap-path-prefix or --remap-path-prefix=crate
                let parts: Vec<&str> = arg_str.splitn(2, '=').collect();
                if parts.len() == 2 && parts[1] == "crate" {
                    strategy = RemapStrategy::CrateRelative;
                } else if parts.len() == 1 {
                    // flag without value defaults to crate relative
                    strategy = RemapStrategy::CrateRelative;
                } else {
                    return Err(format!("Invalid value for --remap-path-prefix: {}", parts[1]));
                }
            } else if input_path.is_none() {
                input_path = Some(PathBuf::from(arg));
            } else {
                return Err(format!("Unexpected argument: {}", arg_str));
            }
        }
        let input_path = input_path.ok_or_else(|| "Missing input path argument".to_string())?;
        Ok(Config { strategy, input_path })
    }
}

/// Remap an absolute path to a crate‑relative representation.
fn remap_path(path: &Path) -> PathBuf {
    // Find the first component that looks like a crate name (heuristic: a directory containing Cargo.toml).
    // For this PoC we simply strip everything up to the last two components.
    let components: Vec<_> = path.components().collect();
    if components.len() <= 2 {
        return PathBuf::from(path);
    }
    // Keep the last two components (e.g., "crate_name/src/lib.rs").
    let mut remapped = PathBuf::new();
    for comp in &components[components.len() - 2..] {
        remapped.push(comp);
    }
    remapped
}

fn apply_strategy(path: &Path, strategy: &RemapStrategy) -> PathBuf {
    match strategy {
        RemapStrategy::None => PathBuf::from(path),
        RemapStrategy::CrateRelative => {
            if path.is_absolute() {
                remap_path(path)
            } else {
                PathBuf::from(path)
            }
        }
    }
}

fn main() {
    let args = env::args_os();
    let config = match Config::from_args(args) {
        Ok(cfg) => cfg,
        Err(e) => {
            eprintln!("Error parsing arguments: {}", e);
            eprintln!("Usage: prog [--remap-path-prefix[=crate]] <path>");
            process::exit(1);
        }
    };

    let remapped = apply_strategy(&config.input_path, &config.strategy);
    println!("Original: {}", config.input_path.display());
    println!("Remapped: {}", remapped.display());
}