package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "os"
    "os/exec"
    "path/filepath"
    "sync"
    "time"
)

// ScreenshotService provides full‑page screenshot capability using a headless Chrome binary.
type ScreenshotService struct {
    // pool ensures only a limited number of Chrome processes run concurrently.
    sem   chan struct{}
    mu    sync.Mutex
    cache map[string][]byte // simple in‑memory cache keyed by URL
}

// NewScreenshotService creates a service with a maximum of maxConcurrent Chrome instances.
func NewScreenshotService(maxConcurrent int) *ScreenshotService {
    return &ScreenshotService{
        sem:   make(chan struct{}, maxConcurrent),
        cache: make(map[string][]byte),
    }
}

// Capture navigates to the given URL and returns a PNG screenshot of the full page.
func (s *ScreenshotService) Capture(targetURL string) ([]byte, error) {
    // Check cache first.
    s.mu.Lock()
    if data, ok := s.cache[targetURL]; ok {
        s.mu.Unlock()
        return data, nil
    }
    s.mu.Unlock()

    // Acquire a slot in the semaphore.
    s.sem <- struct{}{}
    defer func() { <-s.sem }()

    // Create a temporary file for Chrome to write the screenshot.
    tmpDir := os.TempDir()
    filePath := filepath.Join(tmpDir, fmt.Sprintf("screenshot-%d.png", time.Now().UnixNano()))
    defer os.Remove(filePath)

    // Build Chrome command. Adjust the binary name if necessary (google-chrome, chromium, etc.).
    cmd := exec.Command(
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=1920,1080",
        "--screenshot="+filePath,
        "--virtual-time-budget=10000",
        targetURL,
    )
    var stderr bytes.Buffer
    cmd.Stderr = &stderr

    if err := cmd.Run(); err != nil {
        return nil, fmt.Errorf("chrome execution failed: %w, details: %s", err, stderr.String())
    }

    // Read the generated PNG.
    data, err := os.ReadFile(filePath)
    if err != nil {
        return nil, fmt.Errorf("reading screenshot failed: %w", err)
    }

    // Store in cache.
    s.mu.Lock()
    s.cache[targetURL] = data
    s.mu.Unlock()

    return data, nil
}

// authMiddleware is a placeholder that checks a simple token query parameter.
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.URL.Query().Get("token")
        if token != "secret" { // In real code, integrate with Grafana auth.
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}

func main() {
    // Initialise the screenshot service with a pool of 2 concurrent Chrome instances.
    svc := NewScreenshotService(2)

    http.Handle("/api/screenshot/fullpage", authMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        url := r.URL.Query().Get("url")
        if url == "" {
            http.Error(w, "missing url parameter", http.StatusBadRequest)
            return
        }
        img, err := svc.Capture(url)
        if err != nil {
            log.Printf("screenshot error: %v", err)
            http.Error(w, "failed to capture screenshot", http.StatusInternalServerError)
            return
        }
        w.Header().Set("Content-Type", "image/png")
        w.Header().Set("Content-Length", fmt.Sprintf("%d", len(img)))
        if _, err := w.Write(img); err != nil {
            log.Printf("write response error: %v", err)
        }
    })))

    // Health check endpoint.
    http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        io.WriteString(w, "ok")
    })

    // Simple JSON description for manual testing.
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        info := map[string]string{"message": "Grafana Screenshot PoC. Use /api/screenshot/fullpage?url=<dashboard>&token=secret"}
        json.NewEncoder(w).Encode(info)
    })

    log.Println("starting server on :8080")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatalf("server failed: %v", err)
    }
}