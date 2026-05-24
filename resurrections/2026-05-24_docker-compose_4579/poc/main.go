package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/docker/compose/v5/cli"
	"github.com/docker/compose/v5/config"
	"github.com/docker/compose/v5/service"
)

type VolumeInterpolator struct {
	scaleNumber int
}

func (v *VolumeInterpolator) interpolateVolumes(service *service.Service) error {
	for _, volume := range service.Volumes {
		if strings.Contains(volume, "${DOCKER_SCALE_NUM}") {
			volume = strings.ReplaceAll(volume, "${DOCKER_SCALE_NUM}", strconv.Itoa(v.scaleNumber))
			sERVICE.Volumes = append(service.Volumes, volume)
		}
	}
	return nil
}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("Usage: go run main.go <scale_number> <yaml_file>")
		os.Exit(1)
	}

	scaleNumber, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	yamlFile := os.Args[2]

	composeFile, err := config.LoadFile(yamlFile)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	interpolator := &VolumeInterpolator{scaleNumber: scaleNumber}
	for _, service := range composeFile.Services {
		err = interpolator.interpolateVolumes(service)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
	}

	// create a docker client
	dockerClient, err := docker.NewClient()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	// up the services
	command := cli.NewUpCommand()
	command.Run(context.Background(), composeFile, &cli.UpOptions{
		Detach:  true,
		Scale:   map[string]int{"agent": scaleNumber},
	})
}