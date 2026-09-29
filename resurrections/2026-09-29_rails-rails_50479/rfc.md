# RFC: Add Thruster to Docker setup to get HTTP/2, X-Sendfile, Caching by default in Rails 8

Summary
The proposal adds a lightweight Go‑based reverse proxy called **Thruster** to the official Rails 8 Docker image. Thruster terminates HTTP/2, injects X‑Sendfile headers, and provides configurable response caching before forwarding traffic to Puma via a Unix socket. Integration is performed with a multi‑stage Dockerfile that builds the Thruster binary using Go 1.22, copies it into the rails:8 base image, and replaces the default entrypoint with a wrapper that starts Thruster then Puma. All changes are optional and gated behind the environment variable `THRUSTER_ENABLED`. The result is a zero‑configuration, production‑ready stack that offers modern HTTP features out‑of‑the‑box while preserving the existing Rails‑Puma workflow for users who prefer a direct setup.

Motivation
Rails applications are frequently deployed behind external load balancers or CDNs that provide HTTP/2, caching, and X‑Sendfile support. However, many developers run containers in environments where such edge services are unavailable (e.g., local development, small VPS, CI pipelines). Without a proxy, Rails defaults to HTTP/1.1, lacks efficient static file off‑loading, and provides no built‑in caching headers, leading to sub‑optimal performance and extra operational overhead. The original Thruster effort was abandoned because of maintenance concerns and limited Docker capabilities. Since 2026, Go 1.22’s `http2.Server` API and Docker BuildKit’s automatic binary caching make embedding a small, self‑contained proxy trivial. Providing this capability directly in the official Docker image reduces friction, standardises best‑practice configurations, and aligns Rails with modern web standards.

Detailed Design
1. **Multi‑stage Dockerfile**
   ```Dockerfile
   # ---- Build Thruster ----
   FROM golang:1.22-alpine AS thruster-builder
   WORKDIR /src
   COPY thruster/ .
   RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/thruster ./cmd/thruster

   # ---- Final Rails Image ----
   FROM rails:8
   COPY --from=thruster-builder /out/thruster /usr/local/bin/thruster
   COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
   RUN chmod +x /usr/local/bin/thruster /usr/local/bin/entrypoint.sh
   ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
   CMD []
   ```
2. **Entry‑point script** (`entrypoint.sh`)
   ```bash
   #!/usr/bin/env bash
   set -e
   if [ "${THRUSTER_ENABLED}" = "true" ]; then
     # Start Thruster in background, listening on 443, forwarding to Puma socket
     thruster \
       -listen :443 \
       -upstream unix:/tmp/puma.sock \
       -http2 true \
       -xsendfile ${THRUSTER_XSENDFILE:-false} \
       -cache ${THRUSTER_CACHE:-false} &
   fi
   # Start Puma (default command from Rails image)
   exec "$@"
   ```
3. **Configuration via env vars**
   * `THRUSTER_ENABLED` – enable/disable proxy (default `false`).
   * `THRUSTER_XSENDFILE` – when `true`, adds `X‑Sendfile` header for static assets.
   * `THRUSTER_CACHE` – when `true`, adds `Cache‑Control: public, max-age=31536000` for fingerprinted assets.
   * `THRUSTER_LOG_LEVEL` – maps to Thruster’s log verbosity, default `info`.
4. **Health Checks**
   * Dockerfile adds `HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000/health || exit 1` for Puma.
   * Thruster health is exposed on `/__thruster/health` and is queried by a secondary script that combines both statuses.
5. **Logging**
   Thruster forwards its logs to stdout in JSON format compatible with Rails logger, enabling aggregation via existing log pipelines.
6. **Backward Compatibility**
   Existing Dockerfiles that do not copy the new entrypoint or set `THRUSTER_ENABLED` continue to run Puma directly, ensuring no breaking change for current users.

Drawbacks
* **Increased image size** – Adding the Go binary (~5 MB) and extra scripts raises the final image size by ~7 MB, which may be noticeable for edge‑device deployments.
* **Additional process** – Running Thruster adds a second PID to the container, requiring careful resource limits and may affect containers that rely on a single‑process model for simplicity.
* **Maintenance overhead** – The Rails core team must keep the Thruster source in sync with Go releases and audit security patches for the binary.
* **Potential port conflict** – By default Thruster binds to 443; users that already expose another TLS terminator must override the listen address.

Alternatives
1. **Rely on external reverse proxies** (nginx, Caddy, Traefik). This avoids adding code to Rails but re‑introduces the original operational complexity the RFC aims to eliminate.
2. **Puma native HTTP/2 support** – Contribute HTTP/2 directly to Puma. This would be ideal but is a longer‑term effort and does not address X‑Sendfile or caching.
3. **Use a pre‑built lightweight proxy image** (e.g., `caddy:alpine`) as a sidecar container. This keeps the Rails image untouched but requires orchestration changes and additional network hops.
4. **Webpacker/Asset pipeline enhancements** – Emit proper caching headers from Rails itself. This solves caching but not HTTP/2 termination.

Unresolved Questions
* **Security hardening** – How should TLS certificates be provisioned for Thruster inside the container? Should we support automatic Let's Encrypt integration or expect users to mount certs?
* **Performance impact** – What is the latency overhead of proxying via Unix socket compared to direct Puma connections, especially under high concurrency?
* **Feature flag granularity** – Should X‑Sendfile and caching be toggled per‑route rather than globally via env vars?
* **Observability** – Do we need a dedicated metrics endpoint (Prometheus) for Thruster, and who will maintain those exporters?
* **Versioning** – How will future Go version upgrades be coordinated without breaking existing builds?
* **Community ownership** – Which team will become the maintainer of the Thruster source within the Rails repository?

---

*RFC generated by Resurrection Bot 🧬*
