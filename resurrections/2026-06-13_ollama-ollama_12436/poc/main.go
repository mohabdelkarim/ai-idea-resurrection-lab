package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/spf13/cobra"
)

type Config struct {
	LocalOnlyMode bool `json:"local_only_mode"`
}

func main() {
	var config Config
	localOnlyMode := flag.Bool("local-only", false, "disable remote/cloud features")
	flag.Parse()

	config.LocalOnlyMode = *localOnlyMode

	if config.LocalOnlyMode {
		log.Println("Running in local-only mode")
	} else {
		log.Println("Running with remote/cloud features enabled")
	}

	// Initialize gin router
	r := gin.Default()

	// Define a route to test remote features
	r.GET("/test-remote", func(c *gin.Context) {
		if config.LocalOnlyMode {
			c.JSON(200, gin.H{"message": "Remote features are disabled"})
		} else {
			// Simulate a remote call
			c.JSON(200, gin.H{"message": "Remote call successful"})
		}
	})

	// Start the server
	err := r.Run(":8080")
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func loadConfig() (*Config, error) {
	config := &Config{}
	// Load config from file or other sources
	// For simplicity, assume a JSON file
	configFile, err := os.Open("config.json")
	if err != nil {
		return nil, err
	}
	defer configFile.Close()

	decoder := json.NewDecoder(configFile)
	err = decoder.Decode(config)
	if err != nil {
		return nil, err
	}

	return config, nil
}

func initConfig(cmd *cobra.Command) {
	var configFile string
	cmd.Flags().StringVarP(&configFile, "config", "c", "config.json", "path to config file")

	cmd.Run = func(cmd *cobra.Command, args []string) {
		config, err := loadConfig()
		if err != nil {
			log.Fatalf("Failed to load config: %v", err)
		}

		// Use the loaded config
		if config.LocalOnlyMode {
			log.Println("Running in local-only mode")
		} else {
			log.Println("Running with remote/cloud features enabled")
		}
	}
}