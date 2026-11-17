package main

import (
    "errors"
    "fmt"
    "strings"
)

// Pod represents a minimal subset of k8s Pod needed for the demo.
type Pod struct {
    Name      string
    Namespace string
    Labels    map[string]string
    NodeName  string
}

// Node represents a minimal subset of k8s Node.
type Node struct {
    Name string
}

// TopologySpreadConstraint mirrors the k8s API with an added CrossNamespace flag.
type TopologySpreadConstraint struct {
    MaxSkew        int
    TopologyKey    string // e.g., "hostname"
    Selector       map[string]string
    CrossNamespace bool
}

// matchesSelector checks if pod's labels satisfy the constraint's selector.
func matchesSelector(pod Pod, selector map[string]string) bool {
    for k, v := range selector {
        if podVal, ok := pod.Labels[k]; !ok || podVal != v {
            return false
        }
    }
    return true
}

// filterPods returns pods that match the selector and, if crossNamespace is false,
// are in the same namespace as the incoming pod.
func filterPods(all []Pod, incoming Pod, c TopologySpreadConstraint) ([]Pod, error) {
    if c.MaxSkew <= 0 {
        return nil, errors.New("MaxSkew must be > 0")
    }
    var filtered []Pod
    for _, p := range all {
        if !matchesSelector(p, c.Selector) {
            continue
        }
        if !c.CrossNamespace && p.Namespace != incoming.Namespace {
            continue
        }
        filtered = append(filtered, p)
    }
    return filtered, nil
}

// calculateScores computes a score per node: lower count -> higher score.
func calculateScores(pods []Pod, nodes []Node, incoming Pod, c TopologySpreadConstraint) (map[string]int, error) {
    filtered, err := filterPods(pods, incoming, c)
    if err != nil {
        return nil, err
    }
    // Count pods per topology domain (node) respecting the topology key.
    counts := make(map[string]int)
    for _, p := range filtered {
        // In this PoC, TopologyKey is assumed to be "hostname" i.e., node name.
        if p.NodeName != "" {
            counts[p.NodeName]++
        }
    }
    // Build scores: nodes with fewer pods get higher score (max 10).
    scores := make(map[string]int)
    maxScore := 10
    for _, n := range nodes {
        cnt := counts[n.Name]
        // Simple scoring: score = maxScore - cnt, but never below 0.
        score := maxScore - cnt
        if score < 0 {
            score = 0
        }
        scores[n.Name] = score
    }
    return scores, nil
}

func main() {
    // Sample data: three nodes, several pods across two namespaces.
    nodes := []Node{{Name: "nodeA"}, {Name: "nodeB"}, {Name: "nodeC"}}
    pods := []Pod{
        {Name: "p1", Namespace: "ns1", Labels: map[string]string{"app": "worker"}, NodeName: "nodeA"},
        {Name: "p2", Namespace: "ns1", Labels: map[string]string{"app": "worker"}, NodeName: "nodeA"},
        {Name: "p3", Namespace: "ns2", Labels: map[string]string{"app": "worker"}, NodeName: "nodeB"},
        {Name: "p4", Namespace: "ns2", Labels: map[string]string{"app": "worker"}, NodeName: "nodeC"},
    }
    // Incoming pod we want to schedule.
    incoming := Pod{Name: "new", Namespace: "ns1", Labels: map[string]string{"app": "worker"}}

    // Constraint without cross-namespace (default behavior).
    c1 := TopologySpreadConstraint{MaxSkew: 1, TopologyKey: "hostname", Selector: map[string]string{"app": "worker"}, CrossNamespace: false}
    scores1, err := calculateScores(pods, nodes, incoming, c1)
    if err != nil {
        fmt.Printf("error: %v\n", err)
        return
    }
    fmt.Println("Scores without cross-namespace:")
    for n, s := range scores1 {
        fmt.Printf("  %s: %d\n", n, s)
    }

    // Constraint with cross-namespace enabled.
    c2 := TopologySpreadConstraint{MaxSkew: 1, TopologyKey: "hostname", Selector: map[string]string{"app": "worker"}, CrossNamespace: true}
    scores2, err := calculateScores(pods, nodes, incoming, c2)
    if err != nil {
        fmt.Printf("error: %v\n", err)
        return
    }
    fmt.Println(strings.Repeat("-", 30))
    fmt.Println("Scores with cross-namespace:")
    for n, s := range scores2 {
        fmt.Printf("  %s: %d\n", n, s)
    }
}