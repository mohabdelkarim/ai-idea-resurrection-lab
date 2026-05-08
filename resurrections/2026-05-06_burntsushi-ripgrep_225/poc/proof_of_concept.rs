//! PoC: in-process decompression for ripgrep
//! Demonstrates searching compressed .gz/.zst files without spawning an external process.
//! Uses the `flate2` and `zstd` crates for decompression.

use std::fs::File;
use std::io::{self, BufRead, BufReader, Read};
use std::path::Path;

// In a real ripgrep integration these would be cargo dependencies:
// flate2 = "1"
// zstd = "0.13"
// For this PoC we use a trait-object approach to keep it self-contained.

/// Supported compressed formats detected by file extension.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CompressedFormat {
    Gzip,
    Zstd,
    Plain,
}

impl CompressedFormat {
    pub fn from_path(path: &Path) -> Self {
        match path.extension().and_then(|e| e.to_str()) {
            Some("gz") => Self::Gzip,
            Some("zst") | Some("zstd") => Self::Zstd,
            _ => Self::Plain,
        }
    }
}

/// Open a file and return a boxed BufReader that transparently decompresses.
pub fn open_maybe_compressed(path: &Path) -> io::Result<Box<dyn BufRead>> {
    let file = File::open(path)?;
    match CompressedFormat::from_path(path) {
        CompressedFormat::Gzip => {
            // flate2::read::GzDecoder wraps the raw file reader.
            // Uncomment when flate2 is available:
            // use flate2::read::GzDecoder;
            // Ok(Box::new(BufReader::new(GzDecoder::new(file))))
            //
            // Stub for PoC without the actual crate:
            eprintln!("[PoC] Would decompress {} as gzip", path.display());
            Ok(Box::new(BufReader::new(file)))
        }
        CompressedFormat::Zstd => {
            // zstd::Decoder wraps the raw file reader.
            // Uncomment when zstd is available:
            // use zstd::stream::read::Decoder as ZstdDecoder;
            // Ok(Box::new(BufReader::new(ZstdDecoder::new(file)?)))
            eprintln!("[PoC] Would decompress {} as zstd", path.display());
            Ok(Box::new(BufReader::new(file)))
        }
        CompressedFormat::Plain => Ok(Box::new(BufReader::new(file))),
    }
}

/// Search for `pattern` in a file, printing matching lines with file:line context.
/// Preserves the original file name in output (unlike pipe-based decompression).
pub fn search_file(path: &Path, pattern: &str) -> io::Result<usize> {
    let reader = open_maybe_compressed(path)?;
    let mut matches = 0usize;
    for (line_no, line_result) in reader.lines().enumerate() {
        let line = line_result?;
        if line.contains(pattern) {
            println!("{}:{}: {}", path.display(), line_no + 1, line);
            matches += 1;
        }
    }
    Ok(matches)
}

/// Walk a directory recursively, searching each file.
pub fn search_dir(dir: &Path, pattern: &str) -> io::Result<usize> {
    let mut total = 0usize;
    if dir.is_file() {
        return search_file(dir, pattern);
    }
    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            total += search_dir(&path, pattern)?;
        } else {
            match search_file(&path, pattern) {
                Ok(n) => total += n,
                Err(e) => eprintln!("[warn] skipping {}: {}", path.display(), e),
            }
        }
    }
    Ok(total)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: {} <pattern> <path...>", args[0]);
        std::process::exit(1);
    }
    let pattern = &args[1];
    let mut total_matches = 0usize;
    for path_str in &args[2..] {
        let path = Path::new(path_str);
        match search_dir(path, pattern) {
            Ok(n) => total_matches += n,
            Err(e) => eprintln!("[error] {}: {}", path_str, e),
        }
    }
    eprintln!("\nTotal matches: {}", total_matches);
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_plain_file_search() {
        let mut f = NamedTempFile::new().unwrap();
        writeln!(f, "hello world").unwrap();
        writeln!(f, "foo bar").unwrap();
        writeln!(f, "hello again").unwrap();
        let count = search_file(f.path(), "hello").unwrap();
        assert_eq!(count, 2);
    }

    #[test]
    fn test_format_detection() {
        assert_eq!(CompressedFormat::from_path(Path::new("a.gz")), CompressedFormat::Gzip);
        assert_eq!(CompressedFormat::from_path(Path::new("b.zst")), CompressedFormat::Zstd);
        assert_eq!(CompressedFormat::from_path(Path::new("c.txt")), CompressedFormat::Plain);
    }
}
