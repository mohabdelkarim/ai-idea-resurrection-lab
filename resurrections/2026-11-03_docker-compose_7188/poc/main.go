package main

import (
    "errors"
    "fmt"
    "net"
    "strconv"
    "strings"
)

// PortRange represents a host port interval for a given protocol.
type PortRange struct {
    HostIP   string
    Start    int
    End      int
    Target   int // container port
    Protocol string
}

// parsePortSpec parses a string like "127.0.0.1:32768-61000:5432".
func parsePortSpec(spec string) (PortRange, error) {
    parts := strings.Split(spec, ":")
    if len(parts) != 3 {
        return PortRange{}, errors.New("invalid port spec format")
    }
    ip := parts[0]
    // validate IP
    if ip != "" && net.ParseIP(ip) == nil {
        return PortRange{}, fmt.Errorf("invalid IP: %s", ip)
    }
    rangePart := parts[1]
    targetPort, err := strconv.Atoi(parts[2])
    if err != nil {
        return PortRange{}, fmt.Errorf("invalid target port: %w", err)
    }
    var start, end int
    if strings.Contains(rangePart, "-") {
        bounds := strings.Split(rangePart, "-")
        if len(bounds) != 2 {
            return PortRange{}, errors.New("invalid range part")
        }
        start, err = strconv.Atoi(bounds[0])
        if err != nil {
            return PortRange{}, fmt.Errorf("invalid start port: %w", err)
        }
        end, err = strconv.Atoi(bounds[1])
        if err != nil {
            return PortRange{}, fmt.Errorf("invalid end port: %w", err)
        }
        if start > end {
            return PortRange{}, errors.New("start port greater than end port")
        }
    } else {
        start, err = strconv.Atoi(rangePart)
        if err != nil {
            return PortRange{}, fmt.Errorf("invalid port: %w", err)
        }
        end = start
    }
    return PortRange{HostIP: ip, Start: start, End: end, Target: targetPort, Protocol: "tcp"}, nil
}

// overlaps returns true if two PortRanges intersect on host ports.
func overlaps(a, b PortRange) bool {
    if a.HostIP != b.HostIP {
        return false // different bind addresses are considered separate
    }
    return a.Start <= b.End && b.Start <= a.End
}

// findFreePort scans a range and returns the first port not in used set.
func findFreePort(r PortRange, used map[int]bool) (int, error) {
    for p := r.Start; p <= r.End; p++ {
        if !used[p] {
            return p, nil
        }
    }
    return 0, errors.New("no free ports in range")
}

func main() {
    // Simulated service port specs
    specs := []string{
        "127.0.0.1:32768-61000:5432",
        "127.0.0.1:32768-61000:5432",
        "0.0.0.0:8080:80",
    }

    var ranges []PortRange
    for _, s := range specs {
        pr, err := parsePortSpec(s)
        if err != nil {
            fmt.Printf("failed to parse %s: %v\n", s, err)
            return
        }
        ranges = append(ranges, pr)
    }

    // Detect overlaps and assign free ports where needed
    used := make(map[int]bool)
    for i, r := range ranges {
        // check against previously allocated ports
        conflict := false
        for j := 0; j < i; j++ {
            if overlaps(r, ranges[j]) {
                // any overlap means conflict on the whole interval
                conflict = true
                break
            }
        }
        if conflict {
            free, err := findFreePort(r, used)
            if err != nil {
                fmt.Printf("service %d has no free port: %v\n", i, err)
                continue
            }
            fmt.Printf("service %d conflict detected, assigning free host port %d\n", i, free)
            used[free] = true
        } else {
            // allocate the first port of the range for simplicity
            used[r.Start] = true
            fmt.Printf("service %d allocated host port %d\n", i, r.Start)
        }
    }
}