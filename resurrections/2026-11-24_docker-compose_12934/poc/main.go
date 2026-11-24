package main

import (
    "bytes"
    "encoding/json"
    "errors"
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
    "os"
    "sync"
    "testing"
    "net/http/httptest"
)

// Engine defines the minimal operations required by compose.
type Engine interface {
    Start(containerID string) error
    Stop(containerID string) error
    Status(containerID string) (string, error)
}

// engineRegistry holds all available engine providers keyed by driver name.
var (
    registryMu sync.RWMutex
    engineRegistry = make(map[string]func() Engine)
)

// RegisterEngine registers a factory for a given driver.
func RegisterEngine(driver string, factory func() Engine) {
    registryMu.Lock()
    defer registryMu.Unlock()
    engineRegistry[driver] = factory
}

// GetEngine returns an Engine implementation for the requested driver.
func GetEngine(driver string) (Engine, error) {
    registryMu.RLock()
    defer registryMu.RUnlock()
    if f, ok := engineRegistry[driver]; ok {
        return f(), nil
    }
    return nil, fmt.Errorf("engine driver %s not found", driver)
}

// AppleEngine implements Engine by delegating to the Apple container runtime HTTP API.
type AppleEngine struct {
    client *http.Client
    endpoint string // base URL of the Apple runtime, e.g., http://localhost:2375
}

// NewAppleEngine creates a new AppleEngine with the given endpoint.
func NewAppleEngine(endpoint string) *AppleEngine {
    return &AppleEngine{client: &http.Client{}, endpoint: endpoint}
}

// apiRequest is a helper to send JSON payloads and decode JSON responses.
func (a *AppleEngine) apiRequest(method, path string, payload interface{}, resp interface{}) error {
    var body []byte
    var err error
    if payload != nil {
        body, err = json.Marshal(payload)
        if err != nil {
            return fmt.Errorf("marshal payload: %w", err)
        }
    }
    req, err := http.NewRequest(method, a.endpoint+path, bytes.NewReader(body))
    if err != nil {
        return fmt.Errorf("create request: %w", err)
    }
    req.Header.Set("Content-Type", "application/json")
    res, err := a.client.Do(req)
    if err != nil {
        return fmt.Errorf("http request: %w", err)
    }
    defer res.Body.Close()
    if res.StatusCode >= 300 {
        data, _ := ioutil.ReadAll(res.Body)
        return fmt.Errorf("api error %d: %s", res.StatusCode, string(data))
    }
    if resp != nil {
        dec := json.NewDecoder(res.Body)
        if err := dec.Decode(resp); err != nil {
            return fmt.Errorf("decode response: %w", err)
        }
    }
    return nil
}

// Start sends a start command to the Apple runtime.
func (a *AppleEngine) Start(containerID string) error {
    if containerID == "" {
        return errors.New("containerID cannot be empty")
    }
    path := fmt.Sprintf("/containers/%s/start", containerID)
    return a.apiRequest(http.MethodPost, path, nil, nil)
}

// Stop sends a stop command.
func (a *AppleEngine) Stop(containerID string) error {
    if containerID == "" {
        return errors.New("containerID cannot be empty")
    }
    path := fmt.Sprintf("/containers/%s/stop", containerID)
    return a.apiRequest(http.MethodPost, path, nil, nil)
}

// Status retrieves the current state of the container.
func (a *AppleEngine) Status(containerID string) (string, error) {
    if containerID == "" {
        return "", errors.New("containerID cannot be empty")
    }
    var result struct{ State string `json:"state"` }
    path := fmt.Sprintf("/containers/%s/json", containerID)
    if err := a.apiRequest(http.MethodGet, path, nil, &result); err != nil {
        return "", err
    }
    return result.State, nil
}

// init registers the Apple engine provider.
func init() {
    RegisterEngine("apple", func() Engine { return NewAppleEngine("http://localhost:2375") })
}

// main demonstrates simple usage based on an environment variable.
func main() {
    driver := os.Getenv("COMPOSE_DRIVER")
    if driver == "" {
        driver = "apple"
    }
    eng, err := GetEngine(driver)
    if err != nil {
        log.Fatalf("failed to get engine: %v", err)
    }
    // Example container ID – in real usage this would come from compose parsing.
    cid := "example123"
    if err := eng.Start(cid); err != nil {
        log.Printf("start error: %v", err)
    } else {
        log.Printf("container %s started", cid)
    }
    state, err := eng.Status(cid)
    if err != nil {
        log.Printf("status error: %v", err)
    } else {
        log.Printf("container %s state: %s", cid, state)
    }
    if err := eng.Stop(cid); err != nil {
        log.Printf("stop error: %v", err)
    } else {
        log.Printf("container %s stopped", cid)
    }
}

// ---- Unit Tests ----
func TestAppleEngineLifecycle(t *testing.T) {
    // Mock Apple runtime API.
    mux := http.NewServeMux()
    mux.HandleFunc("/containers/example/start", func(w http.ResponseWriter, r *http.Request) {
        if r.Method != http.MethodPost {
            t.Errorf("expected POST, got %s", r.Method)
        }
        w.WriteHeader(http.StatusNoContent)
    })
    mux.HandleFunc("/containers/example/stop", func(w http.ResponseWriter, r *http.Request) {
        if r.Method != http.MethodPost {
            t.Errorf("expected POST, got %s", r.Method)
        }
        w.WriteHeader(http.StatusNoContent)
    })
    mux.HandleFunc("/containers/example/json", func(w http.ResponseWriter, r *http.Request) {
        if r.Method != http.MethodGet {
            t.Errorf("expected GET, got %s", r.Method)
        }
        resp := map[string]string{"state": "running"}
        json.NewEncoder(w).Encode(resp)
    })
    server := httptest.NewServer(mux)
    defer server.Close()

    engine := NewAppleEngine(server.URL)
    if err := engine.Start("example"); err != nil {
        t.Fatalf("start failed: %v", err)
    }
    state, err := engine.Status("example")
    if err != nil {
        t.Fatalf("status failed: %v", err)
    }
    if state != "running" {
        t.Fatalf("unexpected state: %s", state)
    }
    if err := engine.Stop("example"); err != nil {
        t.Fatalf("stop failed: %v", err)
    }
}