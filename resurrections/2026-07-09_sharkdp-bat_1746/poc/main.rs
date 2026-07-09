use std::env;
use nu_ansi_term::{Colour, Style};
use std::error::Error;
fn main() -> Result<(), Box<dyn Error>> {
    let dark_theme = env::var("BAT_THEME_DARK").unwrap_or("default-dark".to_string());
    let light_theme = env::var("BAT_THEME_LIGHT").unwrap_or("default-light".to_string());
    let termenv = terminal_colorsaurus::TermEnv::new();
    let is_dark = termenv.is_dark();
    let theme = if is_dark { &dark_theme } else { &light_theme };
    println!("Using theme: {}", theme);
    Ok(())
}