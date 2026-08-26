# RFC: Setting container hostname to `service_name-xx` instead of container-id

Summary
-----
Introduce an optional `hostname_template` field to Docker Compose service definitions that allows automatic generation of container hostnames in the form `<service_name>-<index>`. The template is resolved at compose time using the service name and the replica index, and the resulting hostname is passed to Docker Engine via the stable `--hostname` flag. A corresponding CLI flag `--hostname-template` can override the file setting. This RFC outlines the motivation, design, drawbacks, alternatives, and open questions.

Motivation
----------
Historically, containers launched by Docker Compose inherit a hostname derived from the container ID, which is opaque and hinders human‑readable debugging, log correlation, and service discovery in mixed‑environment clusters. Projects often rely on predictable hostnames for intra‑service communication, especially when using legacy tools that resolve hostnames via `/etc/hosts` rather than DNS. Docker Engine 24.0 now exposes a stable `--hostname` option and the Go SDK supports per‑container hostname configuration, removing the technical blocker that caused the original proposal to be abandoned. Adding a declarative `hostname_template` aligns Compose with these engine capabilities, improves operational ergonomics, and reduces the need for post‑creation scripting.

Detailed Design
---------------
1. **Schema Extension**: Add `hostname_template` (type: string) to the service object in the Compose spec (v3.9+). The field accepts Go‑template‑like placeholders `{{service}}` and `{{index}}`. Example:
   ```yaml
   services:
     web:
       image: nginx
       deploy:
         replicas: 3
       hostname_template: "{{service}}-{{index}}"
   ```
   Validation ensures the template resolves to a DNS‑compatible name (max 63 characters, alphanumeric + hyphens).
2. **Parser Changes**: Extend the Go YAML parser in `compose-go` to read the new field, store it in the internal `ServiceConfig` struct, and expose it via the public API.
3. **Resolution Logic**: During the project generation phase, for each replica `i` (starting at 1), compute `hostname = strings.ReplaceAll(template, "{{service}}", serviceName)` then replace `{{index}}` with `strconv.Itoa(i)`. If the template is omitted, fallback to the existing behavior (no explicit hostname).
4. **Engine Interaction**: When constructing `container.Config` for `ContainerCreate`, set `Hostname: computedHostname`. The Docker Engine 24.0 SDK will propagate this to the container's `/etc/hostname` and `/etc/hosts`.
5. **CLI Override**: Add a global flag `--hostname-template` to `docker compose up` that, if present, overrides any per‑service template. The flag accepts the same placeholder syntax.
6. **Testing**: Implement unit tests for template parsing, validation, and edge cases (empty template, invalid characters, index out of range). Add integration tests that spin up a multi‑replica service on Docker Engine 24.0 and assert that `docker exec <id> hostname` returns the expected value.
7. **Documentation**: Update the Compose reference guide with a new section describing `hostname_template`, usage examples, and the CLI flag. Provide migration notes for existing projects.

Drawbacks
--------
* **Complexity**: Introducing templating adds parsing overhead and a new source of user error (e.g., invalid characters). The implementation must guard against injection attacks, though the placeholder set is limited.
* **Compatibility**: Older Docker Engine versions (<24.0) ignore the hostname field, resulting in containers falling back to default hostnames. Users must ensure engine compatibility.
* **Replica Index Semantics**: The index starts at 1, which may differ from other tools that start at 0, potentially causing confusion.

Alternatives
-----------
1. **Explicit `hostname` per replica**: Users could manually set `hostname` for each replica via `container_name` patterns, but this is verbose and error‑prone.
2. **External DNS / Service Mesh**: Rely on a service mesh (e.g., Consul) to provide stable names, eliminating the need for container‑level hostnames. However, this adds external dependencies.
3. **Post‑creation script**: Run a script after `compose up` that renames containers via `docker rename`. This is brittle and not declarative.

Unresolved Questions
--------------------
1. **Index Base**: Should the index start at 0 or 1? The proposal chooses 1 for readability, but community feedback may prefer 0.
2. **Collision Handling**: If a user provides a template that could generate duplicate hostnames across services, should Compose emit a warning or error?
3. **Cross‑Compose Projects**: How should hostname uniqueness be enforced when multiple Compose projects run on the same Docker host?
4. **Future Template Features**: Do we expose additional placeholders (e.g., `{{project}}`)? Adding more may increase utility but also complexity.
5. **Engine Fallback**: Should Compose attempt a best‑effort fallback (e.g., set container name) when the engine does not support `--hostname`?

This RFC seeks approval to proceed with the schema change, implementation, testing, and documentation updates outlined above.

---

*RFC generated by Resurrection Bot 🧬*
