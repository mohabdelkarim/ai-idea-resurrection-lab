package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/hashicorp/terraform/internal/backend"
	"github.com/hashicorp/terraform/internal/command"
	"github.com/hashicorp/terraform/internal/configs"
	"github.com/hashicorp/terraform/internal/init"
	"github.com/hashicorp/terraform/internal/plans"
	"github.com/hashicorp/terraform/internal/state"
	"github.com/hashicorp/terraform/internal/terraform"
)

func main() {
	// Check if the plan file path is provided as an argument
	if len(os.Args) != 2 {
		log.Fatal("Usage: terraform-show <plan_file>")
	}
	planFile := os.Args[1]

	// Load the plan file
	plan, err := plans.Load(planFile)
	if err != nil {
		log.Fatalf("Error loading plan file: %v", err)
	}

	// Initialize the Terraform working directory
	err = init.Init("", true, false, false)
	if err != nil {
		log.Fatalf("Error initializing Terraform: %v", err)
	}

	// Create a new Terraform context
	ctx := terraform.NewContext()

	// Load the state
	state, err := state.LoadStateFile()
	if err != nil {
		log.Fatalf("Error loading state: %v", err)
	}

	// Show the plan
	err = command.ShowPlan(ctx, plan, state)
	if err != nil {
		log.Fatalf("Error showing plan: %v", err)
	}
}

func Init(dir string, backend bool, reinit bool) error {
	// Get the current working directory
	pwd, err := os.Getwd()
	if err != nil {
		return err
	}

	// Change to the specified directory
	if dir != "" {
		if err := os.Chdir(dir); err != nil {
			return err
		}
	}

	// Reinitialize the backend if required
	if reinit {
		if err := backend.Reinitialize(); err != nil {
			return err
		}
	}

	// Load the configuration
	config, err := configs.Load(dir)
	if err != nil {
		return err
	}

	// Initialize the backend
	if backend {
		if err := backend.Init(config); err != nil {
			return err
		}
	}

	return nil
}