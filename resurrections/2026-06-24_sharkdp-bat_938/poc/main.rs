use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::process::Command;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let crate_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
    let mut cargo_toml = File::create("Cargo.toml")?;
    writeln!(cargo_toml, "[package]")?;
    writeln!(cargo_toml, "name = \"bat\"")?;
    writeln!(cargo_toml, "version = \"0.1.0\"")?;
    writeln!(cargo_toml, "edition = \"2021\"")?;
    writeln!(cargo_toml, "")?;
    writeln!(cargo_toml, "[dependencies]")?;
    writeln!(cargo_toml, "clap = \"4.6.1\"")?;
    writeln!(cargo_toml, "nu-ansi-term = \"0.50.3\"")?;
    writeln!(cargo_toml, "")?;
    writeln!(cargo_toml, "[features]")?;
    writeln!(cargo_toml, "default = ["]?;
    writeln!(cargo_toml, "    \"application\",")?;
    writeln!(cargo_toml, "    \"git\",")?;
    writeln!(cargo_toml, "]")?;
    writeln!(cargo_toml, "application = [")?;
    writeln!(cargo_toml, "    \"bugreport\",")?;
    writeln!(cargo_toml, "    \"build-assets\",")?;
    writeln!(cargo_toml, "    \"minimal-application\",")?;
    writeln!(cargo_toml, "]")?;
    writeln!(cargo_toml, "git = [")?;
    writeln!(cargo_toml, "    \"git2\",")?;
    writeln!(cargo_toml, "]")?;

    let output = Command::new("cargo")
        .arg("build")
        .env("CARGO_MANIFEST_DIR", &crate_dir)
        .output()?;
    if !output.status.success() {
        println!("Failed to build: {}", String::from_utf8_lossy(&output.stderr));
        return Err("Build failed".into());
    }
    Ok(())
}