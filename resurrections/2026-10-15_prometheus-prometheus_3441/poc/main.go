package main

import (
    "errors"
    "fmt"
    "log"
    "os"
    "strconv"
    "syscall"
    "testing"
)

// parseUIDGID reads PROMETHEUS_UID and PROMETHEUS_GID from the environment.
// It returns the numeric IDs or an error if the values are malformed.
func parseUIDGID() (uid, gid int, err error) {
    uidStr := os.Getenv("PROMETHEUS_UID")
    gidStr := os.Getenv("PROMETHEUS_GID")
    if uidStr == "" && gidStr == "" {
        // No overrides requested.
        return -1, -1, nil
    }
    if uidStr == "" || gidStr == "" {
        return -1, -1, errors.New("both PROMETHEUS_UID and PROMETHEUS_GID must be set")
    }
    uid, err = strconv.Atoi(uidStr)
    if err != nil {
        return -1, -1, fmt.Errorf("invalid UID %s: %w", uidStr, err)
    }
    gid, err = strconv.Atoi(gidStr)
    if err != nil {
        return -1, -1, fmt.Errorf("invalid GID %s: %w", gidStr, err)
    }
    if uid < 0 || gid < 0 {
        return -1, -1, errors.New("UID and GID must be non‑negative")
    }
    return uid, gid, nil
}

// dropPrivileges attempts to set the process UID/GID.
func dropPrivileges(uid, gid int) error {
    if uid == -1 && gid == -1 {
        // Nothing to do.
        return nil
    }
    // Set GID first according to POSIX recommendations.
    if err := syscall.Setgid(gid); err != nil {
        return fmt.Errorf("failed to set GID to %d: %w", gid, err)
    }
    if err := syscall.Setuid(uid); err != nil {
        return fmt.Errorf("failed to set UID to %d: %w", uid, err)
    }
    return nil
}

func main() {
    uid, gid, err := parseUIDGID()
    if err != nil {
        log.Fatalf("error parsing UID/GID: %v", err)
    }
    if err := dropPrivileges(uid, gid); err != nil {
        log.Fatalf("error dropping privileges: %v", err)
    }
    // Placeholder for actual Prometheus startup logic.
    fmt.Println("Prometheus would start now under UID/GID", uid, gid)
}

// Unit tests for the parsing logic.
func TestParseUIDGID_NoEnv(t *testing.T) {
    os.Unsetenv("PROMETHEUS_UID")
    os.Unsetenv("PROMETHEUS_GID")
    uid, gid, err := parseUIDGID()
    if err != nil {
        t.Fatalf("expected no error, got %v", err)
    }
    if uid != -1 || gid != -1 {
        t.Fatalf("expected default -1 values, got uid=%d gid=%d", uid, gid)
    }
}

func TestParseUIDGID_Invalid(t *testing.T) {
    os.Setenv("PROMETHEUS_UID", "abc")
    os.Setenv("PROMETHEUS_GID", "1000")
    _, _, err := parseUIDGID()
    if err == nil {
        t.Fatalf("expected error for invalid UID")
    }
}

func TestParseUIDGID_Valid(t *testing.T) {
    os.Setenv("PROMETHEUS_UID", "1001")
    os.Setenv("PROMETHEUS_GID", "1002")
    uid, gid, err := parseUIDGID()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if uid != 1001 || gid != 1002 {
        t.Fatalf("unexpected values uid=%d gid=%d", uid, gid)
    }
}