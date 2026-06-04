package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
)

func main() {
	var rootCmd = &cobra.Command{
		Use:   "uninstall",
		Short: "Uninstall ollama",
		Run: func(cmd *cobra.Command, args []string) {
			err := uninstall()
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("ollama uninstalled successfully")
		},
	}

	if err := rootCmd.Execute(); err != nil {
		log.Fatal(err)
	}
}

func uninstall() error {
	// Define the directories and files to remove
	dirsToRemove := []string{
		"/usr/local/bin/ollama",
		"/etc/ollama",
	}

	filesToRemove := []string{
		"/usr/local/share/ollama/ollama",
	}

	// Remove directories
	for _, dir := range dirsToRemove {
		err := os.RemoveAll(dir)
		if err != nil {
			return fmt.Errorf("failed to remove directory %s: %w", dir, err)
		}
	}

	// Remove files
	for _, file := range filesToRemove {
		err := os.Remove(file)
		if err != nil && !os.IsNotExist(err) {
			return fmt.Errorf("failed to remove file %s: %w", file, err)
		}
	}

	// Remove any remaining config files
	configDir := filepath.Join(os.Getenv("HOME"), ".ollama")
	if _, err := os.Stat(configDir); err == nil {
		err = os.RemoveAll(configDir)
		if err != nil {
			return fmt.Errorf("failed to remove config directory %s: %w", configDir, err)
		}
	}

	return nil
}