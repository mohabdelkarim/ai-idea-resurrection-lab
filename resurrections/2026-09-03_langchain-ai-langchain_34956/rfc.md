# RFC: Enable Exporting Select Agent Metrics to Customer-facing Dashboards in Real-Time

1. Summary
LangChain will add a first‑class observability layer that exports selected agent metrics (latency per step, token usage, success/failure counts) to external customer‑facing dashboards in real time. The implementation introduces a MetricsExporter that conforms to the OpenTelemetry MeterProvider API, a set of built‑in Counter and Histogram instruments, and an extension of the existing CallbackHandler to emit these metrics during agent execution. Users can configure the exporter backend (Prometheus, Datadog, generic HTTP, or custom) via LangChain settings, and the system will operate asynchronously and thread‑safely.

2. Motivation
Current LangChain deployments expose metrics only through LangSmith, which is internal and does not satisfy many enterprise customers that require real‑time visibility in their own monitoring stacks. The lack of a unified telemetry SDK forced developers to write ad‑hoc instrumentation, leading to duplicated effort and inconsistent data. With OpenTelemetry 1.24 now stable and LangChain v0.2 offering an extensible CallbackManager, the technical obstacles that previously blocked a clean implementation have been removed. Providing a standardized, low‑overhead export path will:
- Enable operators to set SLOs on agent latency and token consumption.
- Reduce debugging time by surfacing failures instantly.
- Align LangChain with industry observability best practices, increasing adoption in regulated environments.

3. Detailed Design
**3.1 MetricsExporter**
- Implements `opentelemetry.metrics.MeterProvider`.
- Registers two primary instruments:
  * `agent_step_latency` (Histogram, unit=seconds)
  * `agent_token_usage` (Counter, unit=tokens)
- Optional instruments: `agent_success`, `agent_failure` (Counters).
- Exporter selection is driven by a new `LangChainMetricsConfig` dataclass:
  ```python
  class LangChainMetricsConfig:
      backend: Literal["prometheus", "datadog", "http", "none"]
      endpoint: str | None = None
      headers: dict[str, str] | None = None
      push_interval: int = 10  # seconds
  ```
- Concrete exporter classes (`PrometheusMetricsExporter`, `DatadogMetricsExporter`, `HttpMetricsExporter`) inherit from a common `BaseMetricsExporter` that handles async batch pushes using `asyncio.create_task`.

**3.2 Callback Integration**
- Extend `langchain.callbacks.base.CallbackHandler` with `MetricsCallbackHandler`.
- On `on_agent_start`, record start timestamp in a contextvar.
- On `on_agent_end`, compute elapsed time, retrieve `token_usage` from the agent's `run` result, and call `MetricsExporter.record_latency` and `record_tokens`.
- The handler respects async execution; all metric calls are `await`‑ed if the exporter is async.

**3.3 Lifecycle Management**
- `LangChainRuntime.start()` will instantiate the configured exporter and register it with the global OpenTelemetry SDK.
- `LangChainRuntime.shutdown()` will flush pending metrics and cancel background push tasks.
- Exporter objects are thread‑safe via an `asyncio.Lock` protecting instrument updates.

**3.4 Pluggability**
- Users can inject additional `CallbackHandler`s via `CallbackManager.add_handler` without modifying core code.
- A `CustomMetricsHandler` example is provided in documentation to illustrate third‑party exporter integration.

4. Drawbacks
- Adding an OpenTelemetry dependency increases the package size (~2 MB) and may introduce version conflicts for projects already using a different OpenTelemetry version.
- Real‑time export incurs a small CPU and network overhead; in high‑throughput scenarios this could marginally affect latency.
- Misconfiguration of push intervals or endpoint authentication could lead to metric loss or security exposure.

5. Alternatives
- **Polling Approach**: Periodically query LangChain internal state via a REST endpoint. This avoids SDK dependencies but introduces latency and requires additional server code.
- **Log‑Based Export**: Emit JSON logs and rely on external log shippers (e.g., Fluentd) to parse metrics. Simpler but less efficient and harder to guarantee ordering.
- **LangSmith Extension**: Extend LangSmith to forward metrics to external backends. This keeps a single source of truth but forces all users to adopt LangSmith, which many enterprises avoid for cost or compliance reasons.

6. Unresolved Questions
- How should we handle multi‑process deployments (e.g., gunicorn workers) where each process creates its own exporter instance? Should we provide a shared collector mode?
- What default push interval balances freshness and overhead for typical workloads?
- Should we expose a per‑agent enable/disable flag to allow selective metric collection?
- How will authentication be standardized across backends (API keys, OAuth, mTLS) without leaking credentials in user code?
- Is there a need for a fallback buffer when the export endpoint is temporarily unavailable, and what size should that buffer have?

---

*RFC generated by Resurrection Bot 🧬*
