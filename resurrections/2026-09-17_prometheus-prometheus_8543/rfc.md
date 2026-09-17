# RFC: Load scrape configs from multiple files

1. Summary
Prometheus will gain the ability to load scrape configurations from multiple separate files using a glob pattern. A new top‑level field `scrape_config_files` (type []string) will be added to the main configuration file. At reload time the ConfigReloader will invoke a new `ScrapeConfigLoader` that expands the glob patterns, parses each file with yaml.v3, validates uniqueness of `job_name` across all files, merges the resulting `ScrapeConfig` objects into the existing slice, and applies the new configuration atomically. This change enables operators to modularise their scrape definitions, improves maintainability, and leverages Go 1.21's `fs.Glob` and the refactored reload hooks introduced in 2024.

2. Motivation
Large Prometheus deployments often maintain hundreds of scrape jobs. Keeping all jobs in a single `scrape_configs` block makes the main YAML file unwieldy, hard to review in code reviews, and difficult to generate programmatically. Operators currently resort to templating or external scripts to split configurations, which introduces a source of error and diverges from the declarative nature of Prometheus. A native multi‑file approach would:
* Reduce configuration file size and improve readability.
* Allow teams to own separate files for distinct services or environments.
* Enable CI pipelines to validate individual job files in isolation.
* Align Prometheus with other CNCF projects (e.g., Loki, Grafana Agent) that already support multi‑file config loading.
The recent Go 1.21 enhancements (`embed.FS` and `fs.Glob`) and the 2024 refactor of the reload pipeline make this addition low‑risk and performant.

3. Detailed Design
* **Config schema change**: Add `scrape_config_files: []string` to the root config struct with yaml tag `scrape_config_files`. This field is optional; if omitted, existing single‑file behaviour is unchanged.
* **ScrapeConfigLoader struct**:
```go
type ScrapeConfigLoader struct {
    FS   fs.FS        // Allows testing with an in‑memory FS
    Globs []string
}
func (l *ScrapeConfigLoader) Load() ([]*config.ScrapeConfig, error)
```
  * Resolve each glob using `fs.Glob(l.FS, pattern)`.
  * For each matched file, read the content via `fs.ReadFile` and decode into a temporary struct `struct{ ScrapeConfigs []*config.ScrapeConfig `yaml:"scrape_configs"` }` using yaml.v3's streaming decoder to keep memory usage low.
  * Collect all `ScrapeConfig` objects, checking that `job_name` is unique across the entire set. On duplicate, return a descriptive error.
  * Return the merged slice.
* **Integration with ConfigReloader**:
  * Extend `ConfigReloader` with method `LoadScrapeConfigs(cfg *Config) error` that invokes the loader, replaces `cfg.ScrapeConfigs` with the merged slice, and propagates any error to the reload flow, preserving atomicity.
* **Validation**: Re‑use existing validation logic (`ValidateScrapeConfig`) on each loaded config. Errors abort the reload and leave the previous configuration intact.
* **Testing**:
  * Unit tests for glob expansion, duplicate detection, parsing errors, and successful merge.
  * Integration test that triggers a live reload via HTTP `/-/reload` and verifies that new jobs appear.
* **Documentation**: Update the official configuration guide with a section "Loading scrape configs from multiple files" including examples:
```yaml
scrape_config_files:
  - "scrape_jobs/*.yaml"
  - "extra_jobs/*.yml"
```

4. Drawbacks
* **Complexity**: Introducing glob expansion adds a small amount of runtime complexity and potential for subtle bugs (e.g., overlapping globs). Careful testing is required.
* **Performance impact**: On reload, multiple files are read and parsed; however, the streaming parser and the fact that reloads are infrequent keep overhead negligible (<10 ms for typical workloads).
* **Backward compatibility**: Existing configurations that already contain `scrape_configs` will continue to work; however, if both `scrape_configs` and `scrape_config_files` are present, the loader will prioritize `scrape_config_files` and ignore the inline block, which must be documented to avoid confusion.

5. Alternatives
* **Single‑file include directive**: Introduce a custom `include` YAML tag that pulls in other files. This would require a custom unmarshaler and would not benefit from the new `fs.Glob` API.
* **Environment variable substitution**: Allow a single file to reference other files via env vars. This approach is less explicit and harder to validate.
* **External pre‑processor**: Recommend users run a templating tool (e.g., `gomplate`) before starting Prometheus. This shifts responsibility to operators and does not provide atomic reload semantics.
All alternatives either increase operational burden or lack native atomic validation, making the proposed multi‑file loader the most robust solution.

6. Unresolved Questions
* Should we support a mix of `scrape_configs` (inline) and `scrape_config_files` simultaneously, merging both, or enforce exclusivity? A decision will affect documentation and error handling.
* How should we handle file ordering when duplicate job names appear in later globs? The current design aborts on any duplicate, but an option to let later files override earlier ones could be considered.
* Do we need to expose a flag to disable glob expansion for security‑hardened deployments where file system access must be tightly controlled?
* Should we add a configurable limit on the number of files or total size to guard against denial‑of‑service attacks during reload?
These questions will be addressed during the implementation sprint.

---

*RFC generated by Resurrection Bot 🧬*
