use std::collections::HashMap;
use std::error::Error;
use std::fmt;

use crossterm::style::{Color, PrintColor, ResetColor};
use crossterm::terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen};
use crossterm::{event, execute, terminal};
use unicode_segmentation::UnicodeSegmentation;

const POWERLINE_SEPARATOR: &str = "";

#[derive(Debug)]
enum PowerlineError {
    CrosstermError(crossterm::ErrorKind),
    IoError(std::io::Error),
}

impl fmt::Display for PowerlineError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            PowerlineError::CrosstermError(e) => write!(f, "Crossterm error: {}", e),
            PowerlineError::IoError(e) => write!(f, "IO error: {}", e),
        }
    }
}

impl Error for PowerlineError {}

fn main() -> Result<(), Box<dyn Error>> {
    enable_raw_mode()?;
    let mut stdout = std::io::stdout();
    execute!(stdout, EnterAlternateScreen)?;

    let segments = vec![
        ("Hello", Color::Blue),
        ("World", Color::Red),
    ];

    print_powerline_prompt(&segments)?;

    disable_raw_mode()?;
    execute!(stdout, LeaveAlternateScreen)?;
    Ok(())
}

fn print_powerline_prompt(segments: &[(String, Color)]) -> Result<(), PowerlineError> {
    let mut stdout = std::io::stdout();
    let mut prev_color = Color::Default;

    for (i, (segment, color)) in segments.iter().enumerate() {
        if *color != prev_color {
            execute!(stdout, PrintColor(*color))?;
        }
        write!(stdout, "{}", segment)?;
        if *color != prev_color {
            execute!(stdout, ResetColor)?;
            prev_color = *color;
        }
        if i < segments.len() - 1 {
            execute!(stdout, PrintColor(Color::Yellow))?;
            write!(stdout, " {}", POWERLINE_SEPARATOR)?;
            execute!(stdout, ResetColor)?;
        }
    }
    Ok(())
}