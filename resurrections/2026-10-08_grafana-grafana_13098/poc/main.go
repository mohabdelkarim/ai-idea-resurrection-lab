package dashboard

import (
    "encoding/json"
    "fmt"
    "net/url"
    "strings"
    "sync"
)

// DashboardState holds the state of a dashboard, including row collapse info.
type DashboardState struct {
    // Other fields omitted for brevity.
    RowCollapse map[string]bool `json:"rowCollapse"`
    mu          sync.RWMutex
}

// NewDashboardState creates a DashboardState with default values.
func NewDashboardState() *DashboardState {
    return &DashboardState{RowCollapse: make(map[string]bool)}
}

// SetRowCollapse sets the collapse state for a given row ID.
func (ds *DashboardState) SetRowCollapse(rowID string, collapsed bool) {
    ds.mu.Lock()
    defer ds.mu.Unlock()
    ds.RowCollapse[rowID] = collapsed
}

// GetRowCollapse retrieves the collapse state for a given row ID.
func (ds *DashboardState) GetRowCollapse(rowID string) bool {
    ds.mu.RLock()
    defer ds.mu.RUnlock()
    if val, ok := ds.RowCollapse[rowID]; ok {
        return val
    }
    // Default: not collapsed.
    return false
}

// Serialize converts the DashboardState to a URL-friendly string.
func (ds *DashboardState) Serialize() (string, error) {
    ds.mu.RLock()
    defer ds.mu.RUnlock()
    // Marshal only the RowCollapse map.
    data, err := json.Marshal(ds.RowCollapse)
    if err != nil {
        return "", fmt.Errorf("failed to marshal row collapse state: %w", err)
    }
    // Encode as base64 URL safe string (using standard library).
    // For simplicity, we use plain JSON and URL-encode it.
    encoded := url.QueryEscape(string(data))
    return encoded, nil
}

// Deserialize populates the DashboardState from a URL string.
func (ds *DashboardState) Deserialize(encoded string) error {
    ds.mu.Lock()
    defer ds.mu.Unlock()
    if strings.TrimSpace(encoded) == "" {
        // No parameter – keep defaults.
        return nil
    }
    decoded, err := url.QueryUnescape(encoded)
    if err != nil {
        return fmt.Errorf("failed to unescape row collapse param: %w", err)
    }
    var m map[string]bool
    if err := json.Unmarshal([]byte(decoded), &m); err != nil {
        return fmt.Errorf("failed to unmarshal row collapse state: %w", err)
    }
    ds.RowCollapse = m
    return nil
}

// URLStateHandler manages synchronization between DashboardState and URL.
type URLStateHandler struct {
    state *DashboardState
    // In a real implementation this would reference a router or history manager.
}

// NewURLStateHandler creates a new handler.
func NewURLStateHandler(state *DashboardState) *URLStateHandler {
    return &URLStateHandler{state: state}
}

// Register registers the handler – placeholder for actual routing logic.
func (h *URLStateHandler) Register() error {
    // No-op in this PoC.
    return nil
}

// SyncToURL updates the URL with the current state.
func (h *URLStateHandler) SyncToURL() (string, error) {
    serialized, err := h.state.Serialize()
    if err != nil {
        return "", err
    }
    // Build a fake URL for demonstration.
    u := url.URL{Path: "/dashboard", RawQuery: fmt.Sprintf("rowCollapse=%s", serialized)}
    return u.String(), nil
}

// HandleToggle simulates a user toggling a row's collapse state.
func (h *URLStateHandler) HandleToggle(rowID string) (string, error) {
    // Flip the current state.
    current := h.state.GetRowCollapse(rowID)
    h.state.SetRowCollapse(rowID, !current)
    // Sync to URL.
    return h.SyncToURL()
}

// ---- Unit test simulation (would be in *_test.go in real code) ----
func exampleUsage() {
    ds := NewDashboardState()
    handler := NewURLStateHandler(ds)
    // Simulate loading from URL with no param.
    if err := ds.Deserialize(""); err != nil {
        fmt.Println("deserialize error:", err)
    }
    // User collapses row "row-1".
    url1, err := handler.HandleToggle("row-1")
    if err != nil {
        fmt.Println("error handling toggle:", err)
    } else {
        fmt.Println("URL after toggle row-1:", url1)
    }
    // Simulate a new page load with the generated URL.
    parsed, _ := url.Parse(url1)
    params := parsed.Query().Get("rowCollapse")
    ds2 := NewDashboardState()
    if err := ds2.Deserialize(params); err != nil {
        fmt.Println("deserialize error on new load:", err)
    }
    fmt.Println("Row-1 collapsed?", ds2.GetRowCollapse("row-1"))
}

func main() {
    exampleUsage()
}