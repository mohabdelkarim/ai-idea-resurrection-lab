use clap::{Parser, Command, Arg, ArgMatches, Shell};
use std::env;
use std::fs::File;
use std::io::Write;
use std::path::Path;

#[derive(Parser)]
struct Zoxide {
    #[clap(subcommand)]
    subcommand: Option<Subcommand>,
}

#[derive(clap::Subcommand)]
enum Subcommand {
    #[clap(name = "add")]
    Add {
        #[clap(value_parser)]
        path: String,
    },
    #[clap(name = "remove")]
    Remove {
        #[clap(value_parser)]
        path: String,
    },
    #[clap(name = "list")]
    List,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let matches = Zoxide::parse();
    match matches.subcommand {
        Some(Subcommand::Add { path }) => {
            println!("Adding {} to zoide", path);
        }
        Some(Subcommand::Remove { path }) => {
            println!("Removing {} from zoide", path);
        }
        Some(Subcommand::List) => {
            println!("Listing zoide entries");
        }
        None => {
            if let Some(completion) = matches.get_one::<String>("completion") {
                generate_completion(completion)?;
            }
        }
    }
    Ok(())
}

fn generate_completion(shell: &str) -> Result<(), Box<dyn std::error::Error>> {
    let out = Command::new("zoxide")
        .version("1.0")
        .author("Ajeet D Souza")
        .about("A zoxide tool")
        .subcommand(
            Command::new("add")
                .about("Add a new entry")
                .arg(Arg::new("path").required(true)),
        )
        .subcommand(
            Command::new("remove")
                .about("Remove an entry")
                .arg(Arg::new("path").required(true)),
        )
        .subcommand(Command::new("list").about("List all entries"))
        .completion_script(Shell::Zsh);
    let mut file = File::create(Path::new("zoxide.zsh"))?;
    write!(file, "{}", out)?;
    Ok(())
}