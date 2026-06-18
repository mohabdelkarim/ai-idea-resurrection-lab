package main

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"strings"
)

// DataSourceEnv represents a data source for reading .env files
type DataSourceEnv struct {
	Path      string   `hcl:"path"`
	Variables []string `hcl:"variables"`
}

// ReadEnvFile reads a .env file and returns a map of variables
func ReadEnvFile(path string) (map[string]string, error) {
	envVars := make(map[string]string)

	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			return nil, errors.New("invalid env file format")
		}

		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])

		envVars[key] = value
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return envVars, nil
}

func main() {
	// Example usage
	path := ".env"
	envVars, err := ReadEnvFile(path)
	if err != nil {
		fmt.Printf("Error reading .env file: %v\n", err)
		return
	}

	for key, value := range envVars {
		fmt.Printf("export %s=%s\n", key, value)
	}
}