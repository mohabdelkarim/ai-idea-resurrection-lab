package main

import (
    "bufio"
    "errors"
    "flag"
    "fmt"
    "io"
    "os"
    "strings"
    "text/template"
)

// RunOptions represents minimal options for our PoC.
type RunOptions struct {
    FromFile string
    Image    string
    Cmd      []string
}

// loadManifest reads the file content.
func loadManifest(path string) (string, error) {
    f, err := os.Open(path)
    if err != nil {
        return "", err
    }
    defer f.Close()
    var sb strings.Builder
    r := bufio.NewReader(f)
    for {
        line, err := r.ReadString('\n')
        sb.WriteString(line)
        if err != nil {
            if errors.Is(err, io.EOF) {
                break
            }
            return "", err
        }
    }
    return sb.String(), nil
}

// renderTemplate applies the image tag to the manifest using go templates.
func renderTemplate(manifest string, img string) (string, error) {
    tmpl, err := template.New("manifest").Parse(manifest)
    if err != nil {
        return "", err
    }
    var sb strings.Builder
    data := map[string]string{"Image": img}
    if err := tmpl.Execute(&sb, data); err != nil {
        return "", err
    }
    return sb.String(), nil
}

func main() {
    // Define flags.
    fromFile := flag.String("from-file", "", "Path to manifest yaml file")
    image := flag.String("image", "", "Container image to inject")
    flag.Parse()
    // Remaining args are the command to run in the pod.
    cmd := flag.Args()

    if *fromFile == "" {
        fmt.Fprintln(os.Stderr, "error: --from-file is required")
        os.Exit(1)
    }
    if *image == "" {
        fmt.Fprintln(os.Stderr, "error: --image is required")
        os.Exit(1)
    }

    // Load manifest.
    raw, err := loadManifest(*fromFile)
    if err != nil {
        fmt.Fprintf(os.Stderr, "failed to load manifest: %v\n", err)
        os.Exit(1)
    }

    // Render with image override.
    rendered, err := renderTemplate(raw, *image)
    if err != nil {
        fmt.Fprintf(os.Stderr, "template rendering failed: %v\n", err)
        os.Exit(1)
    }

    // Simulate merging command overrides (append command to container args).
    // For simplicity, just replace a placeholder {{.Cmd}}.
    finalManifest := strings.ReplaceAll(rendered, "{{.Cmd}}", strings.Join(cmd, " "))

    // Output the final manifest that would be sent to the server.
    fmt.Println("--- Final Manifest ---")
    fmt.Println(finalManifest)
}