package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/compose-spec/compose-go/v2"
	"github.com/docker/compose/v5/cli"
	"github.com/docker/compose/v5/config"
	"github.com/docker/compose/v5/service"
	"github.com/spf13/cobra"
)

func main() {
	// Create a new Docker Compose command
	cmd := &cobra.Command{
		Use:   "docker-compose",
		Short: "Docker Compose command",
	}

	// Add a new command to up
	upCmd := &cobra.Command{
		Use:   "up",
		Short: "Bring up containers",
		RunE: func(cmd *cobra.Command, args []string) error {
			// Load the Docker Compose file
			composeFile, err := config.LoadFile("docker-compose.yml")
			if err != nil {
				return err
			}

			// Get the service
			serviceName := "agent"
			serviceDef, err := composeFile.Service(serviceName)
			if err != nil {
				return err
			}

			// Get the scale number
			scaleNumber, err := getScaleNumber()
			if err != nil {
				return err
			}

			// Templating the volume mount
			templatedVolumes, err := templateVolumes(serviceDef.Volumes, scaleNumber)
			if err != nil {
				return err
			}

			// Update the service with templated volumes
			serviceDef.Volumes = templatedVolumes

			// Up the service
			return upService(serviceDef)
		},
	}

	// Add the up command to the root command
	cmd.AddCommand(upCmd)

	// Execute the command
	if err := cmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func getScaleNumber() (int, error) {
	// For demonstration purposes, get the scale number from an environment variable
	scaleNumberStr := os.Getenv("DOCKER_SCALE_NUM")
	if scaleNumberStr == "" {
		return 0, errors.New("DOCKER_SCALE_NUM environment variable is not set")
	}

	scaleNumber, err := strconv.Atoi(scaleNumberStr)
	if err != nil {
		return 0, err
	}

	return scaleNumber, nil
}

func templateVolumes(volumes []service.VolumeConfig, scaleNumber int) ([]service.VolumeConfig, error) {
	templatedVolumes := make([]service.VolumeConfig, 0, len(volumes))

	for _, volume := range volumes {
		// Template the volume mount
		templatedVolume := service.VolumeConfig{
		Type:   volume.Type,
		Source: strings.ReplaceAll(volume.Source, "${DOCKER_SCALE_NUM}", strconv.Itoa(scaleNumber)),
		Target: volume.Target,
		ReadOnly: volume.ReadOnly,
		}

		templatedVolumes = append(templatedVolumes, templatedVolume)
	}

	return templatedVolumes, nil
}

func upService(serviceDef *service.Service) error {
	// For demonstration purposes, just print the service definition
	serviceJson, err := json.MarshalIndent(serviceDef, "", "\t")
	if err != nil {
		return err
	}

	fmt.Println(string(serviceJson))

	return nil
}