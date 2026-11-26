package main

import (
    "encoding/json"
    "log"
    "net/http"
    "sync"
    "time"
)

// MetricMetadata holds basic information about a metric.
type MetricMetadata struct {
    Name string `json:"name"`
    Help string `json:"help"`
    Type string `json:"type"`
    // Timestamp of the last update, used for last‑write‑wins.
    UpdatedAt time.Time `json:"updated_at"`
}

// MetadataStore is a thread‑safe in‑memory store for metric metadata.
type MetadataStore struct {
    mu   sync.RWMutex
    data map[string]MetricMetadata
}

// NewMetadataStore creates an empty store.
func NewMetadataStore() *MetadataStore {
    return &MetadataStore{data: make(map[string]MetricMetadata)}
}

// Set stores metadata, applying last‑write‑wins and logging conflicts.
func (s *MetadataStore) Set(m MetricMetadata) {
    s.mu.Lock()
    defer s.mu.Unlock()
    if existing, ok := s.data[m.Name]; ok {
        if existing.Help != m.Help {
            log.Printf("warning: HELP string for metric %s changed from %q to %q", m.Name, existing.Help, m.Help)
        }
    }
    m.UpdatedAt = time.Now()
    s.data[m.Name] = m
}

// Get returns metadata for a given metric name.
func (s *MetadataStore) Get(name string) (MetricMetadata, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    m, ok := s.data[name]
    return m, ok
}

// List returns all stored metadata.
func (s *MetadataStore) List() []MetricMetadata {
    s.mu.RLock()
    defer s.mu.RUnlock()
    out := make([]MetricMetadata, 0, len(s.data))
    for _, m := range s.data {
        out = append(out, m)
    }
    return out
}

// simulateWrite mimics the TSDB write path, extracting HELP and TYPE from a sample.
func simulateWrite(store *MetadataStore, name, help, typ string) {
    // In real Prometheus this would parse the # HELP and # TYPE lines.
    meta := MetricMetadata{Name: name, Help: help, Type: typ}
    store.Set(meta)
}

func metadataHandler(store *MetadataStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        // If a ?metric= query param is supplied, return that metric only.
        if name := r.URL.Query().Get("metric"); name != "" {
            if m, ok := store.Get(name); ok {
                json.NewEncoder(w).Encode(m)
                return
            }
            http.Error(w, "metric not found", http.StatusNotFound)
            return
        }
        // Otherwise return the full list.
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(store.List())
    }
}

func main() {
    store := NewMetadataStore()

    // Simulate a few writes.
    simulateWrite(store, "http_requests_total", "Total number of HTTP requests.", "counter")
    simulateWrite(store, "cpu_usage_seconds", "CPU usage in seconds.", "gauge")
    // Simulate a conflicting HELP string.
    simulateWrite(store, "http_requests_total", "Number of HTTP requests received.", "counter")

    http.HandleFunc("/api/v1/metadata", metadataHandler(store))
    log.Println("starting server on :8080")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatalf("server failed: %v", err)
    }
}