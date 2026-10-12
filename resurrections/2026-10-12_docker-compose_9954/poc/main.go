package main

import (
    "errors"
    "flag"
    "fmt"
    "os"
    "strings"
)

// UpOptions holds options for the "up" command.
type UpOptions struct {
    Build      bool     // whether to build before up
    BuildArgs  []string // build arguments passed via --build-arg
    Services   []string // services to bring up
    ComposeFile string  // path to compose file
}

// parseBuildArgs is a custom flag.Value implementation that collects multiple --build-arg values.
type buildArgs []string

func (b *buildArgs) String() string { return strings.Join(*b, ",") }
func (b *buildArgs) Set(value string) error {
    if strings.TrimSpace(value) == "" {
        return errors.New("build-arg cannot be empty")
    }
    *b = append(*b, value)
    return nil
}

func main() {
    var opts UpOptions
    var args buildArgs

    // Define flags using the standard library flag package.
    flag.BoolVar(&opts.Build, "build", false, "Build images before starting containers")
    flag.Var(&args, "build-arg", "Set build-time variables (can be used multiple times)")
    flag.StringVar(&opts.ComposeFile, "f", "docker-compose.yml", "Compose file to use")
    // Parse the flags.
    flag.Parse()
    opts.BuildArgs = args
    opts.Services = flag.Args()

    // Simple validation: if --build-arg is provided without --build, warn the user.
    if len(opts.BuildArgs) > 0 && !opts.Build {
        fmt.Fprintln(os.Stderr, "warning: --build-arg provided without --build; arguments will be ignored")
    }

    // Execute the up logic.
    if err := runUp(opts); err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }
}

// runUp performs the core up operation, invoking a mock build when needed.
func runUp(opts UpOptions) error {
    fmt.Printf("Running docker compose up with options: %+v\n", opts)
    if opts.Build {
        if err := mockBuild(opts.BuildArgs, opts.ComposeFile); err != nil {
            return fmt.Errorf("build failed: %w", err)
        }
    }
    // Here we would normally start the containers; for this PoC we just print.
    fmt.Println("Containers started (mock)")
    return nil
}

// mockBuild simulates building images, printing received build arguments.
func mockBuild(buildArgs []string, composeFile string) error {
    fmt.Printf("Building images defined in %s with build arguments:\n", composeFile)
    if len(buildArgs) == 0 {
        fmt.Println("  (none)")
        return nil
    }
    for _, a := range buildArgs {
        // Simple validation: ensure the argument contains an '='.
        if !strings.Contains(a, "=") {
            return fmt.Errorf("invalid build-arg %q, expected KEY=VALUE format", a)
        }
        fmt.Printf("  %s\n", a)
    }
    // Simulate success.
    fmt.Println("Build succeeded (mock)")
    return nil
}