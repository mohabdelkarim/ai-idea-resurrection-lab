import asyncio
import time
import threading
import json
from typing import Callable, Dict, Any, List

# Simple configuration object
class ExporterConfig:
    def __init__(self, backend: str = "custom", endpoint: str = "http://localhost:8000/metrics"):
        self.backend = backend
        self.endpoint = endpoint

# MetricsExporter that mimics OpenTelemetry MeterProvider interface
class MetricsExporter:
    def __init__(self, config: ExporterConfig):
        self.config = config
        self._counters: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        self._running = False
        self._task: asyncio.Task | None = None

    async def _export_loop(self):
        while self._running:
            await asyncio.sleep(5)  # export every 5 seconds
            await self._flush()

    async def _flush(self):
        async with self._lock:
            snapshot = self._counters.copy()
            self._counters.clear()
        # In real implementation, send to backend. Here we just print.
        print(f"[MetricsExporter] Flushing metrics to {self.config.backend}: {snapshot}")

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._export_loop())
        print("[MetricsExporter] Started")

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
        await self._flush()
        print("[MetricsExporter] Stopped")

    async def record(self, name: str, value: float = 1.0):
        async with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

# Simulated CallbackHandler that integrates with MetricsExporter
class AgentCallbackHandler:
    def __init__(self, exporter: MetricsExporter):
        self.exporter = exporter
        self._start_times: Dict[int, float] = {}
        self._lock = threading.Lock()

    def on_step_start(self, step_id: int):
        with self._lock:
            self._start_times[step_id] = time.time()
        print(f"[Callback] Step {step_id} started")

    async def on_step_end(self, step_id: int, tokens_used: int):
        start = None
        with self._lock:
            start = self._start_times.pop(step_id, None)
        if start is None:
            print(f"[Callback] Missing start time for step {step_id}")
            return
        latency = time.time() - start
        await self.exporter.record("agent_latency_seconds", latency)
        await self.exporter.record("agent_tokens_used", tokens_used)
        print(f"[Callback] Step {step_id} ended, latency={latency:.3f}s, tokens={tokens_used}")

# Simple agent simulation that uses the callback handler
class DummyAgent:
    def __init__(self, callback: AgentCallbackHandler):
        self.callback = callback
        self._step_counter = 0

    async def run_step(self):
        step_id = self._step_counter
        self._step_counter += 1
        self.callback.on_step_start(step_id)
        # Simulate work
        await asyncio.sleep(0.1 + 0.2 * (step_id % 3))
        tokens = 10 + step_id * 5
        await self.callback.on_step_end(step_id, tokens)

    async def run(self, steps: int = 5):
        for _ in range(steps):
            await self.run_step()

# Main entry point tying everything together
async def main():
    config = ExporterConfig(backend="custom", endpoint="http://example.com/metrics")
    exporter = MetricsExporter(config)
    await exporter.start()
    callback = AgentCallbackHandler(exporter)
    agent = DummyAgent(callback)
    try:
        await agent.run(steps=10)
    except Exception as e:
        print(f"[Error] Agent execution failed: {e}")
    finally:
        await exporter.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user")