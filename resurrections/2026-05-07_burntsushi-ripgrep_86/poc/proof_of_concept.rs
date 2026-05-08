//! PoC: automatic pager invocation for ripgrep
//! When stdout is a TTY and output exceeds one screen, pipe results through
//! the system pager (less / more / $PAGER) using the `minus` crate approach.
//! This PoC simulates the behaviour without requiring the actual crate.

use std::env;
use std::io::{self, IsTerminal, Write};
use std::process::{Child, Command, Stdio};

/// Detect the preferred pager from environment or fall back to `less`.
pub fn detect_pager() -> String {
    // Respect the user's RIPGREP_PAGER first, then PAGER, then default.
    if let Ok(p) = env::var("RIPGREP_PAGER") {
        if !p.is_empty() { return p; }
    }
    if let Ok(p) = env::var("PAGER") {
        if !p.is_empty() { return p; }
    }
    // `less -R` preserves ANSI colour codes and quits if output fits one screen.
    "less -RF".to_string()
}

/// Spawn the pager process and return a handle + its stdin pipe.
pub fn spawn_pager(pager_cmd: &str) -> io::Result<Child> {
    // Split on whitespace to separate the binary from its flags.
    let mut parts = pager_cmd.split_whitespace();
    let bin = parts.next().unwrap_or("less");
    let flags: Vec<&str> = parts.collect();

    Command::new(bin)
        .args(&flags)
        .stdin(Stdio::piped())
        .spawn()
}

/// A writer that transparently routes output through a pager when stdout is a TTY,
/// or writes directly to stdout when not (e.g. piped to a file).
pub struct PagerWriter {
    pager_process: Option<Child>,
}

impl PagerWriter {
    /// Create a new PagerWriter. Spawns the pager only if stdout is a TTY.
    pub fn new() -> io::Result<Self> {
        let is_tty = io::stdout().is_terminal();
        if is_tty {
            let pager_cmd = detect_pager();
            eprintln!("[PoC] Stdout is a TTY — spawning pager: {}", pager_cmd);
            let child = spawn_pager(&pager_cmd)?;
            Ok(Self { pager_process: Some(child) })
        } else {
            Ok(Self { pager_process: None })
        }
    }

    /// Write a line of output.
    pub fn writeln(&mut self, line: &str) -> io::Result<()> {
        if let Some(ref mut child) = self.pager_process {
            if let Some(ref mut stdin) = child.stdin {
                writeln!(stdin, "{}", line)?;
            }
        } else {
            let stdout = io::stdout();
            writeln!(stdout.lock(), "{}", line)?;
        }
        Ok(())
    }

    /// Flush and wait for the pager to exit.
    pub fn finish(mut self) -> io::Result<()> {
        if let Some(mut child) = self.pager_process.take() {
            // Drop stdin to signal EOF to the pager.
            drop(child.stdin.take());
            child.wait()?;
        }
        Ok(())
    }
}

/// Simulate ripgrep producing N lines of search results.
fn simulate_search_results(n: usize) -> Vec<String> {
    (1..=n)
        .map(|i| format!("src/main.rs:{}: match found for pattern (line {})", i * 3, i))
        .collect()
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    // Accept optional line count argument for testing.
    let line_count: usize = args.get(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(200);

    let results = simulate_search_results(line_count);
    eprintln!("[PoC] Emitting {} lines of search output", results.len());

    let mut writer = PagerWriter::new()?;
    for line in results {
        writer.writeln(&line)?;
    }
    writer.finish()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detect_pager_uses_env() {
        env::set_var("RIPGREP_PAGER", "bat");
        assert_eq!(detect_pager(), "bat");
        env::remove_var("RIPGREP_PAGER");
    }

    #[test]
    fn detect_pager_fallback_to_pager_env() {
        env::remove_var("RIPGREP_PAGER");
        env::set_var("PAGER", "more");
        assert_eq!(detect_pager(), "more");
        env::remove_var("PAGER");
    }

    #[test]
    fn detect_pager_default() {
        env::remove_var("RIPGREP_PAGER");
        env::remove_var("PAGER");
        assert_eq!(detect_pager(), "less -RF");
    }

    #[test]
    fn simulate_results_count() {
        let r = simulate_search_results(10);
        assert_eq!(r.len(), 10);
        assert!(r[0].contains("src/main.rs"));
    }
}
