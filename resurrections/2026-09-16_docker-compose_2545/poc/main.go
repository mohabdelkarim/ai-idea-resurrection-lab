package main

import (
    "bufio"
    "errors"
    "fmt"
    "os"
    "path/filepath"
    "strings"
)

// parseArgsFile reads a file containing lines in VAR=VAL format and returns a map.
func parseArgsFile(filePath string) (map[string]string, error) {
    f, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer f.Close()

    args := make(map[string]string)
    scanner := bufio.NewScanner(f)
    lineNum := 0
    for scanner.Scan() {
        lineNum++
        line := strings.TrimSpace(scanner.Text())
        if line == "" || strings.HasPrefix(line, "#") {
            continue // skip blanks and comments
        }
        parts := strings.SplitN(line, "=", 2)
        if len(parts) != 2 {
            return nil, fmt.Errorf("invalid line %d in %s: %s", lineNum, filePath, line)
        }
        key := strings.TrimSpace(parts[0])
        val := strings.TrimSpace(parts[1])
        if key == "" {
            return nil, fmt.Errorf("empty key at line %d in %s", lineNum, filePath)
        }
        args[key] = val
    }
    if err := scanner.Err(); err != nil {
        return nil, err
    }
    return args, nil
}

// mergeArgs merges fileArgs into explicitArgs, giving precedence to explicitArgs.
func mergeArgs(fileArgs, explicitArgs map[string]string) map[string]string {
    merged := make(map[string]string)
    for k, v := range fileArgs {
        merged[k] = v
    }
    for k, v := range explicitArgs {
        merged[k] = v // explicit overrides file
    }
    return merged
}

func main() {
    // Simulate compose file location for relative path resolution
    composeDir, err := os.Getwd()
    if err != nil {
        fmt.Fprintf(os.Stderr, "failed to get cwd: %v\n", err)
        os.Exit(1)
    }

    // Example args_file entries (could be a single string or list)
    argsFiles := []string{"./example.args", "./more.args"}
    aggregated := make(map[string]string)

    for _, relPath := range argsFiles {
        absPath := filepath.Join(composeDir, relPath)
        fileArgs, err := parseArgsFile(absPath)
        if err != nil {
            // If file not found, continue; in real code you might error out.
            if errors.Is(err, os.ErrNotExist) {
                fmt.Fprintf(os.Stderr, "warning: args file %s does not exist, skipping\n", absPath)
                continue
            }
            fmt.Fprintf(os.Stderr, "error parsing %s: %v\n", absPath, err)
            os.Exit(1)
        }
        // Merge respecting precedence of later files over earlier ones
        aggregated = mergeArgs(aggregated, fileArgs)
    }

    // Explicit build args defined directly in compose
    explicit := map[string]string{"SECRET_TOKEN": "override-token", "API_URL": "https://api.example.com"}

    // Final args with explicit taking precedence over file-derived
    finalArgs := mergeArgs(aggregated, explicit)

    fmt.Println("Aggregated Build Args:")
    for k, v := range finalArgs {
        fmt.Printf("%s=%s\n", k, v)
    }
}