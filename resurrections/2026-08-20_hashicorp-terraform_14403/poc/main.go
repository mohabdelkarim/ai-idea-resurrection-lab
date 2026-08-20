package main

import (
    "bufio"
    "bytes"
    "errors"
    "fmt"
    "os"
    "os/exec"
    "strings"
)

// ResourceDiff represents a diff for a resource during apply.
// In real Terraform it contains many fields; we only model the taint flag.
type ResourceDiff struct {
    Name               string
    Tainted            bool // true if the resource was tainted before apply
    TaintReplacement   bool // internal flag set when taint should trigger destroy‑then‑create
    NeedsCreate        bool // true if a new instance must be created
    NeedsDestroy       bool // true if the old instance must be destroyed
    Provisioners       []ProvisionerConfig
}

type ProvisionerConfig struct {
    When    string // "create" or "destroy"
    Command string
    OnFail  string // "continue" or "fail"
}

// evaluateDiff sets internal flags based on the taint status.
func evaluateDiff(rd *ResourceDiff) error {
    if rd == nil {
        return errors.New("nil ResourceDiff")
    }
    // If the resource is tainted we need to destroy the existing instance
    // and then create a new one.
    if rd.Tainted {
        rd.TaintReplacement = true
        rd.NeedsDestroy = true
        rd.NeedsCreate = true
        fmt.Printf("Resource %s is tainted – will destroy then create\n", rd.Name)
    }
    return nil
}

// runProvisioner executes a single provisioner command.
func runProvisioner(pc ProvisionerConfig) error {
    fmt.Printf("Running %s provisioner: %s\n", pc.When, pc.Command)
    // Use /bin/sh -c to allow shell features.
    cmd := exec.Command("/bin/sh", "-c", pc.Command)
    var outBuf, errBuf bytes.Buffer
    cmd.Stdout = &outBuf
    cmd.Stderr = &errBuf
    if err := cmd.Run(); err != nil {
        fmt.Printf("Provisioner error: %v, stderr: %s\n", err, errBuf.String())
        if strings.ToLower(pc.OnFail) == "continue" {
            fmt.Println("Continuing despite error as per on_failure=continue")
            return nil
        }
        return err
    }
    fmt.Printf("Provisioner output: %s\n", outBuf.String())
    return nil
}

// executeProvisioners runs provisioners filtered by the "when" field.
func executeProvisioners(pcs []ProvisionerConfig, phase string) error {
    for _, pc := range pcs {
        if pc.When != phase {
            continue
        }
        if err := runProvisioner(pc); err != nil {
            return err
        }
    }
    return nil
}

// applyResource simulates the apply lifecycle for a single resource.
func applyResource(rd *ResourceDiff) error {
    if err := evaluateDiff(rd); err != nil {
        return err
    }
    // If we need to destroy, run destroy provisioners first.
    if rd.NeedsDestroy {
        fmt.Printf("--- Destroy phase for %s ---\n", rd.Name)
        if err := executeProvisioners(rd.Provisioners, "destroy"); err != nil {
            return fmt.Errorf("destroy provisioner failed: %w", err)
        }
        // Simulate destruction.
        fmt.Printf("Resource %s destroyed\n", rd.Name)
    }
    // Then create.
    if rd.NeedsCreate {
        fmt.Printf("--- Create phase for %s ---\n", rd.Name)
        if err := executeProvisioners(rd.Provisioners, "create"); err != nil {
            return fmt.Errorf("create provisioner failed: %w", err)
        }
        fmt.Printf("Resource %s created\n", rd.Name)
    }
    return nil
}

func main() {
    // Simulate a null_resource with a destroy provisioner.
    rd := &ResourceDiff{
        Name:    "null_resource.test",
        Tainted: true, // emulate "terraform taint"
        Provisioners: []ProvisionerConfig{{
            When:    "create",
            Command: "echo creating resource",
            OnFail:  "fail",
        }, {
            When:    "destroy",
            Command: "echo destroying resource",
            OnFail:  "continue",
        }},
    }
    if err := applyResource(rd); err != nil {
        fmt.Fprintf(os.Stderr, "apply failed: %v\n", err)
        os.Exit(1)
    }
    // Wait for user to press Enter before exiting (useful when run manually).
    fmt.Println("Press Enter to exit...")
    bufio.NewReader(os.Stdin).ReadString('\n')
}