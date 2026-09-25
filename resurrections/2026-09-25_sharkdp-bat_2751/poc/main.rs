use std::env;
use std::io::{self, Read};

/// Mode of wrapping: by character count or by whole words.
#[derive(Debug, Clone, Copy)]
enum WrapMode {
    Char,
    Word,
}

/// Wrap a single line according to the given mode and terminal width.
fn wrap_line(line: &str, width: usize, mode: WrapMode) -> String {
    if width == 0 {
        return line.to_string();
    }
    match mode {
        WrapMode::Char => {
            // Simple byte‑wise wrap (may split multibyte chars).
            let mut result = String::new();
            let mut start = 0;
            while start < line.len() {
                let end = usize::min(start + width, line.len());
                result.push_str(&line[start..end]);
                if end < line.len() {
                    result.push('\n');
                }
                start = end;
            }
            result
        }
        WrapMode::Word => {
            // Word‑wise wrap using whitespace as delimiter.
            let mut result = String::new();
            let mut current_len = 0usize;
            for word in line.split_whitespace() {
                let word_len = word.chars().count();
                // If the word itself exceeds the width, fall back to char wrap.
                if word_len > width {
                    // Flush current line first.
                    if !result.is_empty() && !result.ends_with('\n') {
                        result.push('\n');
                    }
                    // Char‑wise wrap the long word.
                    let mut start = 0;
                    while start < word.len() {
                        let end = usize::min(start + width, word.len());
                        result.push_str(&word[start..end]);
                        if end < word.len() {
                            result.push('\n');
                        }
                        start = end;
                    }
                    current_len = 0;
                    continue;
                }
                // If adding the word would exceed the width, start a new line.
                if current_len > 0 && current_len + 1 + word_len > width {
                    result.push('\n');
                    current_len = 0;
                } else if current_len > 0 {
                    result.push(' ');
                    current_len += 1; // space
                }
                result.push_str(word);
                current_len += word_len;
            }
            result
        }
    }
}

/// Parse a simple "--wrap=char|word" flag from the command line.
fn parse_wrap_mode() -> Result<WrapMode, String> {
    for arg in env::args().skip(1) {
        if let Some(val) = arg.strip_prefix("--wrap=") {
            return match val.to_ascii_lowercase().as_str() {
                "char" => Ok(WrapMode::Char),
                "word" => Ok(WrapMode::Word),
                _ => Err(format!("Invalid wrap mode: {}", val)),
            };
        }
    }
    // Default to Char mode for backward compatibility.
    Ok(WrapMode::Char)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Determine wrap mode.
    let mode = parse_wrap_mode()?;

    // Read all input from stdin.
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;

    // For demonstration we use a fixed width of 20 columns.
    let width = 20usize;

    // Process each line individually.
    let mut output = String::new();
    for (i, line) in input.lines().enumerate() {
        let wrapped = wrap_line(line, width, mode);
        output.push_str(&wrapped);
        if i + 1 < input.lines().count() {
            output.push('\n');
        }
    }

    // Write result to stdout.
    print!("{}", output);
    Ok(())
}