# RFC: Support full page screenshots via chrome dev tools

1. Summary
Add a first‑class full‑page screenshot capability to Grafana by integrating a headless Chromium automation layer using the go‑chromedp library. The feature will expose a new backend service (ScreenshotService) and an HTTP API (/api/screenshot/fullpage) that accepts a dashboard URL and rendering options, captures the entire page as a PNG, stores it in the existing image cache, and returns the image to the caller. A UI button will be added to the dashboard view to trigger the API and display the result.

2. Motivation
Grafana users frequently need high‑fidelity, shareable images of entire dashboards for reporting, documentation, and incident post‑mortems. Existing export options only capture the visible viewport or individual panels, requiring manual stitching or external tools. In 2018 the effort failed because Chrome DevTools commands were unstable and Grafana lacked a clean headless‑browser abstraction. Since then, Chrome DevTools Protocol (CDP) has matured, go‑chromedp and go‑rod provide stable Go bindings, and Grafana's plugin SDK now supports server‑side processes with sandboxing. Providing a reliable full‑page screenshot directly inside Grafana will reduce friction for users, increase adoption in enterprise reporting, and keep Grafana competitive with other observability platforms.

3. Detailed Design
**Backend Service**
- Create `pkg/services/screenshot/screenshot.go` defining `type ScreenshotService struct { pool *chromedp.Pool }`.
- On startup, initialize a singleton Chromium pool (configurable size, default 2) using `chromedp.NewExecAllocator` with `headless`, `disable-gpu`, and sandbox flags.
- Expose method `CaptureFullPage(ctx context.Context, dashboardURL string, opts CaptureOptions) (image []byte, err error)`.
- Implementation steps:
  1. Acquire a Chrome context from the pool.
  2. Navigate to `dashboardURL` with appropriate auth cookies (inject Grafana session via `network.SetCookie`).
  3. Wait for a DOM element `#dashboard` to be visible and for all panel render promises to settle (use `chromedp.WaitReady`).
  4. Execute CDP command `Page.captureScreenshot` with `fullPage: true` and desired `format: png`.
  5. Return the raw PNG bytes.
- Store the PNG in Grafana's existing image cache (`services/imgcache`) using a deterministic key derived from dashboard UID and timestamp.

**API Endpoint**
- Register `/api/screenshot/fullpage` (POST) in `pkg/api/dashboard.go`.
- Request body: `{ "dashboardUid": "string", "theme": "light|dark", "width": int, "height": int }`.
- Authenticate using the standard Grafana auth middleware; reject if the user lacks `View` permission on the dashboard.
- Resolve the dashboard URL (`/d/{uid}`) with the requested theme and dimensions, then call `ScreenshotService.CaptureFullPage`.
- On success, respond with `Content-Type: image/png` and stream the bytes; on error, return appropriate HTTP status.

**UI Integration**
- Add a new button "Full‑Page Screenshot" to the dashboard toolbar (React component `DashboardHeaderControls`).
- On click, POST to the new endpoint, receive the PNG blob, and open a modal displaying the image with download option.
- Show a loading spinner and handle timeout errors gracefully.

**Resource Management & Security**
- Limit concurrent captures via the pool size; queue additional requests.
- Enforce a maximum screenshot size (e.g., 8000px height) to avoid memory blow‑out.
- Run Chromium under a non‑root user inside a sandboxed Docker container if Grafana is deployed in such an environment.
- Clean up Chrome contexts after each capture to prevent leaks.

4. Drawbacks
- Introduces a heavyweight dependency (Chromium) which increases the binary size and may require additional system packages (libgbm, fonts) on the host.
- Headless Chromium consumes CPU and memory; under heavy load, screenshot requests could degrade overall Grafana performance if not properly throttled.
- Requires careful handling of authentication cookies; mis‑configuration could expose dashboards to unauthorized capture.
- Adds operational complexity: operators must monitor Chromium process health and may need to adjust pool size based on workload.

5. Alternatives
- **External Service**: Offload screenshot generation to a separate microservice (e.g., puppeteer server). This reduces Grafana binary bloat but adds network latency and deployment overhead.
- **Static Rendering**: Use Grafana's existing panel rendering engine to stitch panels together server‑side. This avoids Chromium but cannot guarantee pixel‑perfect fidelity for custom panel plugins.
- **Client‑Side Capture**: Leverage the browser's `html2canvas` library to capture the page client‑side. This is limited by CORS, cross‑origin resources, and may miss lazy‑loaded panels.
- Each alternative trades off fidelity, performance, and operational simplicity; the proposed integrated Chromium approach offers the best balance for a first‑class feature.

6. Unresolved Questions
- What is the optimal default pool size for typical deployments (e.g., 2 vs 4 instances) and how should it be exposed in the Grafana config?
- How should we handle dashboards that contain live streaming panels (e.g., real‑time graphs) – should we capture a static snapshot at request time or provide a configurable delay?
- Are there licensing or security implications of bundling Chromium binaries for certain Linux distributions?
- Should we expose additional CDP options (e.g., device scale factor) in the API for power users?
- Need to define monitoring metrics (captures total, failures, latency) and integrate them into Grafana's existing telemetry.

---

*RFC generated by Resurrection Bot 🧬*
