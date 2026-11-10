package main

import (
    "fmt"
    "net/url"
    "testing"
)

// MustParse parses a URL and panics if the URL is invalid.
// Mirrors other Must* helpers in the stdlib.
func MustParse(s string) *url.URL {
    u, err := url.Parse(s)
    if err != nil {
        panic(fmt.Sprintf("url.MustParse: %v", err))
    }
    return u
}

// Do runs the provided function and panics if it returns an error.
// The generic version works for any return type.
func Do[T any](fn func() (T, error)) T {
    v, err := fn()
    if err != nil {
        panic(fmt.Sprintf("must.Do: %v", err))
    }
    return v
}

// Example usage of MustParse and Do.
func example() {
    // Using MustParse directly.
    u1 := MustParse("https://example.com/path")
    fmt.Println("Parsed URL:", u1)

    // Using generic Do to obtain a parsed URL.
    u2 := Do(func() (*url.URL, error) {
        return url.Parse("https://golang.org")
    })
    fmt.Println("Parsed URL via Do:", u2)
}

// Unit tests for MustParse and Do.
func TestMustParseValid(t *testing.T) {
    got := MustParse("http://localhost")
    if got.Scheme != "http" || got.Host != "localhost" {
        t.Fatalf("unexpected result: %v", got)
    }
}

func TestMustParseInvalid(t *testing.T) {
    defer func() {
        if r := recover(); r == nil {
            t.Fatalf("expected panic for invalid URL")
        }
    }()
    MustParse("://bad_url")
}

func TestDoValid(t *testing.T) {
    val := Do(func() (int, error) {
        return 42, nil
    })
    if val != 42 {
        t.Fatalf("expected 42, got %d", val)
    }
}

func TestDoInvalid(t *testing.T) {
    defer func() {
        if r := recover(); r == nil {
            t.Fatalf("expected panic from Do")
        }
    }()
    Do(func() (string, error) {
        return "", fmt.Errorf("forced error")
    })
}

func main() {
    fmt.Println("Running examples...")
    example()
    // Run tests manually (normally 'go test' would be used)
    var t testing.T
    TestMustParseValid(&t)
    TestMustParseInvalid(&t)
    TestDoValid(&t)
    TestDoInvalid(&t)
}