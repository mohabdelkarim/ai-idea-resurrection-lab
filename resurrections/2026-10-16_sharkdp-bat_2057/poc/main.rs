use std::env;
use std::error::Error;
use std::fmt;
use std::io::{self, Write};

/// Supported shells for completion scripts.
#[derive(Debug, PartialEq)]
enum CompletionShell {
    Bash,
    Zsh,
    Fish,
    PowerShell,
}

impl CompletionShell {
    /// Parse a shell name (case‑insensitive) into the enum.
    fn from_str(s: &str) -> Result<Self, ParseShellError> {
        match s.to_ascii_lowercase().as_str() {
            "bash" => Ok(CompletionShell::Bash),
            "zsh" => Ok(CompletionShell::Zsh),
            "fish" => Ok(CompletionShell::Fish),
            "powershell" | "pwsh" => Ok(CompletionShell::PowerShell),
            _ => Err(ParseShellError(s.to_string())),
        }
    }
}

/// Error returned when an unknown shell name is supplied.
#[derive(Debug)]
struct ParseShellError(String);

impl fmt::Display for ParseShellError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "unsupported shell: {}", self.0)
    }
}

impl Error for ParseShellError {}

/// Generate a minimal completion script for the requested shell.
fn generate_completion(shell: CompletionShell) -> String {
    match shell {
        CompletionShell::Bash => {
            "# Bash completion for bat\n_complete bat 'complete -F _bat_completion'\nfunction _bat_completion {\n    COMPREPLY=( $(compgen -W \"--help --version --completion\" -- ${COMP_WORDS[1]}) )\n}\n".to_string()
        }
        CompletionShell::Zsh => {
            "# Zsh completion for bat\n#compdef bat\n_arguments '--help[Show help]' '--version[Show version]' '--completion[Generate completion script]'\n".to_string()
        }
        CompletionShell::Fish => {
            "# Fish completion for bat\ncomplete -c bat -l help -d 'Show help'\ncomplete -c bat -l version -d 'Show version'\ncomplete -c bat -l completion -d 'Generate completion script'\n".to_string()
        }
        CompletionShell::PowerShell => {
            "# PowerShell completion for bat\nRegister-ArgumentCompleter -CommandName 'bat' -ScriptBlock {\n    param($commandName, $parameterName, $wordToComplete, $commandAst, $fakeBoundParameters)\n    $options = '--help','--version','--completion'\n    $options | Where-Object { $_ -like \"$wordToComplete*\" }\n}\n".to_string()
        }
    }
}

/// Entry point that parses `--completion=<shell>` and prints the script.
fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();
    // Look for an argument that starts with "--completion="
    let mut shell_opt: Option<CompletionShell> = None;
    for arg in &args[1..] {
        if let Some(val) = arg.strip_prefix("--completion=") {
            shell_opt = Some(CompletionShell::from_str(val)?);
            break;
        }
    }
    match shell_opt {
        Some(shell) => {
            let script = generate_completion(shell);
            let stdout = io::stdout();
            let mut handle = stdout.lock();
            handle.write_all(script.as_bytes())?;
        }
        None => {
            eprintln!("Usage: {} --completion=<bash|zsh|fish|powershell>", args[0]);
            return Err("missing --completion argument".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_shell() {
        assert_eq!(CompletionShell::from_str("bash").unwrap(), CompletionShell::Bash);
        assert_eq!(CompletionShell::from_str("ZSH").unwrap(), CompletionShell::Zsh);
        assert!(CompletionShell::from_str("unknown").is_err());
    }

    #[test]
    fn test_generate_bash() {
        let out = generate_completion(CompletionShell::Bash);
        assert!(out.contains("_bat_completion"));
    }

    #[test]
    fn test_generate_zsh() {
        let out = generate_completion(CompletionShell::Zsh);
        assert!(out.starts_with("# Zsh completion"));
    }
}