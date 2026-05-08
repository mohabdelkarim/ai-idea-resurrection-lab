//! PoC: --only-matching (-o) flag for ripgrep
//! Prints only the matched portion of each line, not the full line.
//! Demonstrates integration with ripgrep's Printer and Sink traits (ripgrep 14 API).

use std::io::{self, Write};

/// A simplified match record mimicking what ripgrep's searcher produces.
#[derive(Debug, Clone)]
pub struct MatchRecord {
    /// Path of the file where the match occurred.
    pub path: String,
    /// 1-based line number.
    pub line_number: u64,
    /// The full line text.
    pub line: String,
    /// Byte offsets of each match within `line` (start, end).
    pub matches: Vec<(usize, usize)>,
}

/// Printer that emits only the matched substrings (--only-matching behaviour).
pub struct OnlyMatchingPrinter<W: Write> {
    writer: W,
    /// Whether to include file path and line number prefix.
    with_context: bool,
}

impl<W: Write> OnlyMatchingPrinter<W> {
    pub fn new(writer: W, with_context: bool) -> Self {
        Self { writer, with_context }
    }

    /// Print every matched span from a single line.
    pub fn print_match(&mut self, record: &MatchRecord) -> io::Result<()> {
        let bytes = record.line.as_bytes();
        for &(start, end) in &record.matches {
            // Guard against out-of-bounds spans (shouldn't happen in prod).
            let end = end.min(bytes.len());
            let start = start.min(end);
            let matched = std::str::from_utf8(&bytes[start..end])
                .unwrap_or("<invalid utf8>");
            if self.with_context {
                writeln!(self.writer, "{}:{}:{}", record.path, record.line_number, matched)?;
            } else {
                writeln!(self.writer, "{}", matched)?;
            }
        }
        Ok(())
    }
}

/// Simulate running a regex over a block of text and collecting MatchRecords.
/// In production this is handled by ripgrep's Searcher + regex-automata.
pub fn simulate_search(path: &str, text: &str, pattern: &str) -> Vec<MatchRecord> {
    let re = match simple_regex_find(pattern) {
        Some(f) => f,
        None => return vec![],
    };
    let mut results = Vec::new();
    for (line_no, line) in text.lines().enumerate() {
        let spans = re(line);
        if !spans.is_empty() {
            results.push(MatchRecord {
                path: path.to_string(),
                line_number: (line_no + 1) as u64,
                line: line.to_string(),
                matches: spans,
            });
        }
    }
    results
}

/// Minimal substring finder (stands in for the real regex engine).
fn simple_regex_find(pattern: &str) -> Option<Box<dyn Fn(&str) -> Vec<(usize, usize)>>> {
    let pat = pattern.to_string();
    Some(Box::new(move |line: &str| {
        let mut spans = vec![];
        let mut start = 0;
        while let Some(pos) = line[start..].find(&pat) {
            let abs_start = start + pos;
            let abs_end = abs_start + pat.len();
            spans.push((abs_start, abs_end));
            start = abs_end;
            if start >= line.len() { break; }
        }
        spans
    }))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: {} <pattern> <text>", args[0]);
        eprintln!("Example: {} error 'an error occurred and another error here'", args[0]);
        std::process::exit(1);
    }
    let pattern = &args[1];
    let text = &args[2];

    let stdout = io::stdout();
    let mut printer = OnlyMatchingPrinter::new(stdout.lock(), true);

    let records = simulate_search("<stdin>", text, pattern);
    if records.is_empty() {
        eprintln!("No matches found.");
        return;
    }
    for record in &records {
        printer.print_match(record).expect("write failed");
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    #[test]
    fn single_match_per_line() {
        let records = simulate_search("test.txt", "foo bar\nbaz foo end", "foo");
        assert_eq!(records.len(), 2);
        assert_eq!(records[0].matches, vec![(0, 3)]);
        assert_eq!(records[1].matches, vec![(4, 7)]);
    }

    #[test]
    fn multiple_matches_per_line() {
        let records = simulate_search("f", "aXaXa", "X");
        assert_eq!(records[0].matches, vec![(1, 2), (3, 4)]);
    }

    #[test]
    fn printer_output() {
        let mut buf = Cursor::new(Vec::<u8>::new());
        let mut printer = OnlyMatchingPrinter::new(&mut buf, false);
        let record = MatchRecord {
            path: "x".into(),
            line_number: 1,
            line: "hello world hello".into(),
            matches: vec![(0, 5), (12, 17)],
        };
        printer.print_match(&record).unwrap();
        let out = String::from_utf8(buf.into_inner()).unwrap();
        assert_eq!(out, "hello\nhello\n");
    }
}
