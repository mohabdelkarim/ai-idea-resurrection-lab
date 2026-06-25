use std::env;
use std::path::PathBuf;
use std::process::Command;
use anyhow::{Context, Result};
use xshell::{Shell, Target};

fn main() -> Result<()> {
    let out_dir = env::var("OUT_DIR").context("OUT_DIR not set")?;
    let mut shell = Shell::new();
    shell
        .step("Generate tauri config")?
        .run("cargo tauri config generate")?
        .step("Build tauri app")?
        .env("WEBKIT_DISABLE_COMPOSITING_MODE", "1")
        .run("cargo tauri build")?
        .step("Create output directory")?
        .run(format!("mkdir -p {out_dir}"))?
        .step("Copy build artifacts")?
        .run(format!("cp -r src-tauri/target/debug/bundle/* {out_dir}"))?
    ;
    Ok(())
}

// Define a custom xshell step
struct Step<'a> {
    name: &'a str,
}

impl<'a> Step<'a> {
    fn new(name: &'a str) -> Self {
        Self { name }
    }
}

impl<'a> xshell::Step for Step<'a> {
    fn run(&self, shell: &mut Shell) -> Result<()> {
        shell.comment(self.name);
        Ok(())
    }
}

// Define a custom xshell runner
struct Runner;

impl xshell::Runner for Runner {
    fn run(&self, command: &str) -> Result<()> {
        let status = Command::new("sh")
            .arg("-c")
            .arg(command)
            .status()?;
        if status.success() {
            Ok(())
        } else {
            Err(anyhow::anyhow!("Command failed with status {}", status.code().unwrap_or(-1)))
        }
    }
}

// Define the xshell Shell
struct Shell {
    runner: Runner,
}

impl Shell {
    fn new() -> Self {
        Self { runner: Runner }
    }

    fn step(&mut self, name: &str) -> Step {
        Step::new(name)
    }

    fn run(&mut self, command: &str) -> Result<()> {
        self.runner.run(command)
    }
}

// Define the xshell Target
struct Target;

impl Target {
    fn new() -> Self {
        Self
    }
}

// Define the xshell context
trait Context {
    fn context(&self, message: &str) -> Result<()>;
}

impl Context for xshell::Result<()> {
    fn context(&self, message: &str) -> Result<()> {
        self.context(message)
    }
}