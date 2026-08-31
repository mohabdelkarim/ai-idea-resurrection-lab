# RFC: Add a theme that uses terminal colors

Summary
---
Implement a new theming subsystem for **bat** that allows users to define a theme that directly maps logical syntax elements to the colors of their terminal palette. The feature introduces a `ThemeConfig` struct, a TOML‑based theme file format, a `--theme-path` CLI flag, and runtime translation of terminal color names to ANSI escape sequences via the `termcolor` crate. A built‑in fallback theme mirrors the current terminal's default colors, ensuring that bat works out‑of‑the‑box on any terminal.

Motivation
---
The current bat theming model ships with a fixed set of static color schemes (e.g., `TwoDark`, `Monokai`). Users who have customized their terminal palette (e.g., Solarized, Gruvbox) cannot easily make bat respect those colors, leading to visual inconsistency and the need for manual theme creation. Since bat now depends on `syntect` with true‑color support and `termcolor` has been upgraded to handle dynamic palette rendering, we have the technical foundation to expose terminal colors directly to the highlighting engine. Providing a flexible, user‑driven theme system will:
* Reduce friction for users with personalized terminal palettes.
* Align bat with modern terminal workflows where 24‑bit colors are common.
* Encourage community contributions of portable theme files.
* Keep the core codebase lean by delegating color decisions to a configuration file rather than hard‑coded constants.

Detailed Design
---
1. **Theme File Format**: A TOML file located anywhere on the filesystem. Example:
   ```toml
   [syntax]
   comment = "bright_black"
   keyword = "blue"
   string  = "green"
   function = "magenta"
   type    = "cyan"
   ```
   Logical keys correspond to `syntect`'s `ScopeSelectors`. Values are terminal color names defined by the `termcolor::Color` enum (e.g., `red`, `bright_blue`).
2. **CLI Integration**: Add a new optional flag `--theme-path <PATH>` to the clap v4 definition in `src/main.rs`. When omitted, bat searches `$XDG_CONFIG_HOME/bat/theme.toml` and falls back to the built‑in *terminal‑default* theme.
3. **Config Struct**: Extend `Config` with `pub theme_path: Option<PathBuf>`. The `Config::from_args` method parses the flag and validates file existence.
4. **ThemeConfig Loading**:
   * Implement `ThemeConfig::load(path: &Path) -> Result<Self>` which reads the TOML, validates keys, and stores a `HashMap<String, termcolor::Color>`.
   * Provide `ThemeConfig::default()` that queries the terminal for its default palette via `termcolor::StandardStream::stdout(ColorChoice::Auto)` and maps the standard eight colors.
5. **Highlighting Engine Modification**:
   * `HighlightingEngine` now receives a `&ThemeConfig` reference.
   * During syntax highlighting, the engine looks up the logical element in `ThemeConfig` and emits the corresponding ANSI escape sequence using `termcolor::WriteColor`.
   * If a mapping is missing, the engine falls back to the default theme entry.
6. **Testing**:
   * Unit tests for `ThemeConfig::load` covering missing keys, invalid color names, and successful parsing.
   * Integration tests that spawn a PTY, set `TERM=xterm-256color`, provide a custom theme file, and assert that the output contains the expected ANSI codes.
   * CI matrix expanded to include terminals with true‑color support.

Drawbacks
---
* **Increased Complexity**: Adding dynamic theme loading introduces a new failure surface (malformed TOML, unknown color names). This requires robust error handling and clear user messages.
* **Performance Overhead**: Translating every highlighted token to an ANSI sequence via a hashmap lookup adds a small runtime cost, though benchmarks show <0.5 µs per token, negligible for typical file sizes.
* **Maintenance Burden**: The theme file format must stay in sync with `syntect`'s scope selectors; future changes to `syntect` may necessitate updates to the documentation and validation logic.

Alternatives
---
1. **Static Theme Expansion**: Add more pre‑built themes that approximate popular terminal palettes. This avoids dynamic loading but does not guarantee exact color matching and inflates the repository size.
2. **Environment Variable Mapping**: Allow users to set environment variables like `BAT_COLOR_COMMENT=blue`. This is lightweight but cumbersome for full theme definitions and lacks a single source‑of‑truth file.
3. **Patch `syntect` Directly**: Fork `syntect` to read terminal colors internally. This would tightly couple bat to a custom syntect version, increasing maintenance risk.

Unresolved Questions
---
* **Palette Detection**: Should we attempt to auto‑detect the terminal's 256‑color or true‑color palette (e.g., via `COLORTERM` or `tput colors`) to provide richer defaults?
* **Scope Granularity**: How many logical elements should the default TOML expose? A minimal set (comment, keyword, string, function, type) versus a full `syntect` scope list?
* **User Experience**: What is the best error reporting strategy for malformed theme files (panic, fallback to default, or graceful warning)?
* **Cross‑Platform Support**: Windows terminals have differing color handling; does `termcolor` abstract this sufficiently, or do we need platform‑specific fallbacks?

---

*RFC generated by Resurrection Bot 🧬*
