use std::env;
use std::path::{Path, PathBuf};
use url::Url;
use clap::{App, Arg};
use std::error::Error;
use std::fs;
use std::io;

fn main() -> Result<(), Box<dyn Error>> {
    let matches = App::new("rg")
        .version("1.0")
        .author("Your Name")
        .about("A simple grep tool")
        .arg(Arg::with_name("file_url")
            .long("file-url")
            .help("Print file paths as file URLs"))
        .arg(Arg::with_name("pattern")
            .required(true)
            .help("Pattern to search for"))
        .arg(Arg::with_name("path")
            .required(true)
            .help("Path to search in"))
        .get_matches();

    let pattern = matches.value_of("pattern").unwrap();
    let path = matches.value_of("path").unwrap();
    let file_url = matches.is_present("file_url");

    let re = regex::Regex::new(pattern)?;
    let file_paths = fs::read_dir(path)?;

    for entry in file_paths {
        let entry = entry?;
        let file_path = entry.path();
        if file_path.is_file() {
            let file_content = fs::read_to_string(&file_path)?;
            for line in file_content.lines().enumerate() {
                if re.is_match(line.1) {
                    if file_url {
                        println!("{}", file_url_to_string(&file_path, line.0 + 1));
                    } else {
                        println!("{}:{}", file_path.display(), line.0 + 1);
                    }
                }
            }
        }
    }
    Ok(())
}

fn file_url_to_string(file_path: &Path, line_number: usize) -> String {
    let url = Url::from_file_path(file_path).unwrap();
    format!("{url}#L{line_number}")
}