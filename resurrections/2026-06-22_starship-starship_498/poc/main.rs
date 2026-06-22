use std::collections::HashMap;
use std::error::Error;
use std::fmt;

// Define a module for the prompt
struct Module {
    name: String,
    alignment: String,
}

impl Module {
    fn new(name: String, alignment: String) -> Module {
        Module { name, alignment }
    }
}

// Define a prompt configuration
struct PromptConfig {
    modules: Vec<Module>,
}

impl PromptConfig {
    fn new(modules: Vec<Module>) -> PromptConfig {
        PromptConfig { modules }
    }
}

// Define an error for rendering the prompt
#[derive(Debug)]
enum RenderError {
    InvalidAlignment,
}

impl fmt::Display for RenderError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match *self {
            RenderError::InvalidAlignment => write!(f, "Invalid alignment"),
        }
    }
}

impl Error for RenderError {}

// Render the prompt
fn render_prompt(config: &PromptConfig) -> Result<String, RenderError> {
    let mut rendered_modules = Vec::new();
    let mut right_align = false;

    for module in &config.modules {
        if module.name == "line_break" {
            right_align = false;
            rendered_modules.push("\n".to_string());
            continue;
        }

        let content = format!("{{}}", module.name);
        if module.alignment == "right" {
            right_align = true;
        }

        if right_align {
            rendered_modules.push(format!("\n{}\t{}", "", content));
        } else {
            rendered_modules.push(content);
        }
    }

    Ok(rendered_modules.join(""))
}

fn main() {
    let modules = vec![
        Module::new("Hello".to_string(), "left".to_string()),
        Module::new("World".to_string(), "right".to_string()),
        Module::new("line_break".to_string(), "".to_string()),
        Module::new("This is after line break".to_string(), "left".to_string()),
    ];

    let config = PromptConfig::new(modules);
    match render_prompt(&config) {
        Ok(prompt) => println!("{}", prompt),
        Err(err) => eprintln!("Error rendering prompt: {}", err),
    }
}