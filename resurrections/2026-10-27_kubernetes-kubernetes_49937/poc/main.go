package main

import (
    "context"
    "fmt"
    "net/http"
    "time"
)

// HTTPGetAction represents an HTTP probe action.
// In real Kubernetes it lives in k8s.io/api/core/v1, but this is a simplified version.
type HTTPGetAction struct {
    Path       string // request path
    Port       int    // target port
    Scheme     string // http or https
    HTTPMethod string // optional, GET or HEAD, defaults to GET
}

// ProbeResult indicates success or failure of a probe.
type ProbeResult struct {
    Success bool
    Err     error
}

// executeHTTPProbe performs the HTTP request based on the action.
func executeHTTPProbe(ctx context.Context, action HTTPGetAction) ProbeResult {
    // Default method to GET if not specified.
    method := action.HTTPMethod
    if method == "" {
        method = http.MethodGet
    }
    // Validate allowed methods.
    if method != http.MethodGet && method != http.MethodHead {
        return ProbeResult{false, fmt.Errorf("unsupported http method %s", method)}
    }

    url := fmt.Sprintf("%s://localhost:%d%s", action.Scheme, action.Port, action.Path)
    req, err := http.NewRequestWithContext(ctx, method, url, nil)
    if err != nil {
        return ProbeResult{false, err}
    }
    // For HEAD we don't need a body, but Get works the same way.
    client := &http.Client{Timeout: 5 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return ProbeResult{false, err}
    }
    defer resp.Body.Close()
    // Consider any 2xx as success.
    if resp.StatusCode >= 200 && resp.StatusCode < 300 {
        return ProbeResult{true, nil}
    }
    return ProbeResult{false, fmt.Errorf("unexpected status %d", resp.StatusCode)}
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    // Example GET probe.
    getProbe := HTTPGetAction{
        Path:   "/",
        Port:   8080,
        Scheme: "http",
        // HTTPMethod omitted, defaults to GET.
    }
    result := executeHTTPProbe(ctx, getProbe)
    fmt.Printf("GET probe success: %v, err: %v\n", result.Success, result.Err)

    // Example HEAD probe.
    headProbe := HTTPGetAction{
        Path:       "/healthz",
        Port:       8080,
        Scheme:     "http",
        HTTPMethod: http.MethodHead,
    }
    result = executeHTTPProbe(ctx, headProbe)
    fmt.Printf("HEAD probe success: %v, err: %v\n", result.Success, result.Err)
}