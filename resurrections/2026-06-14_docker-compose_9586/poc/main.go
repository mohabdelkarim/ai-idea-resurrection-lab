package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/docker/buildx"
	"github.com/docker/buildx/builder"
	"github.com/docker/buildx/util/progress"
	"github.com/docker/compose/v5"
	"github.com/docker/compose/v5/config"
	"github.com/docker/compose/v5/docker"
	"github.com/docker/compose/v5/project"
	"github.com/docker/go-units"
	"github.com/moby/buildkit"
	"github.com/moby/buildkit/client"
)

func main() {
	// Initialize a new Docker Compose project
	prj, err := project.NewProject(
		"docker-compose.yml",
		config.LoadFile("docker-compose.yml"),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Get the services defined in the Compose file
	services := prj.Services()

	// Iterate over the services and build them with custom outputs
	for _, service := range services {
		// Create a new BuildKit client
		b, err := buildx.NewBuilder()
		if err != nil {
			log.Fatal(err)
		}

		// Define custom build outputs
		opts := []buildx.Option{
			buildx.WithContext(context.Background()),
			buildx.WithProgress(&progress.Printer{}),
		}

		// Create a new build context
		ctx := context.Background()

		// Build the service with custom outputs
		err = b.Build(ctx, opts...,
			buildx.WithDockerFile(service.Dockerfile),
			buildx.WithTags(service.Tags),
			buildx.WithOutput(buildx.NewDockerOutput(
				"docker://my-registry.com/my-image",
				buildx.WithPush(true),
			)),
		)
		if err != nil {
			log.Fatal(err)
		}
	}
}

type CustomBuildOutput struct {
	Type string `json:"type"`
	Name string `json:"name"`
}

func (c *CustomBuildOutput) UnmarshalJSON(data []byte) error {
	var tmp struct {
		Type string `json:"type"`
		Name string `json:"name"`
	}
	if err := json.Unmarshal(data, &tmp); err != nil {
		return err
	}
	c.Type = tmp.Type
	c.Name = tmp.Name
	return nil
}

func NewDockerOutput(registry string, opts ...buildx.OutputOption) buildx.Output {
	return buildx.NewOutput(
		"docker",
		buildx.WithRegistry(registry),
		opts...,
	)
}