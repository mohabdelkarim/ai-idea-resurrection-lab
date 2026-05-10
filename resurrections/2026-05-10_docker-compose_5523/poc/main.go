package main

import (
	"errors"
	"fmt"
	"os"
	"strings"

	"github.com/docker/compose/api/types"
	"github.com/docker/compose/api/types/container"
	"github.com/docker/compose/command"
	"github.com/docker/compose/utils"
	"github.com/spf13/cobra"
)

func main() {
	cmd, err := composeCmd()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	err = cmd.Execute()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func composeCmd() (*cobra.Command, error) {
	cmd := &cobra.Command{
		Use:   "docker-compose",
		Short: "Define and run multi-container Docker applications",
	}

	cmd.AddCommand(versionCmd())
	cmd.AddCommand(upCmd())
	cmd.AddCommand(downCmd())
	cmd.AddCommand(copyCmd())

	return cmd, nil
}

func copyCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "copy [OPTIONS] SRC DEST",
		Short: "Copy files or directories from SRC to DEST",
		RunE: func(cmd *cobra.Command, args []string) error {
			if len(args) != 2 {
				return errors.New("SRC and DEST must be specified")
			}

			src := args[0]
			dest := args[1]

			composeProject, err := command.ProjectFromEnv()
			if err != nil {
				return err
			}

			services, err := composeProject.Services()
			if err != nil {
				return err
			}

			if len(services) == 0 {
				return errors.New("no services defined")
			}

			containerName := services[0].Name

			err = dockerCopy(containerName, src, dest)
			if err != nil {
				return err
			}

			return nil
		},
	}

	return cmd
}

func dockerCopy(containerName string, src string, dest string) error {
	command := fmt.Sprintf("docker cp %s:%s %s", containerName, src, dest)
	_, err := utils.RunCommand(command)
	if err != nil {
		return err
	}

	return nil
}

func versionCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "version",
		Short: "Print version information",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("1.0.0")
		},
	}

	return cmd
}

func upCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "up",
		Short: "Create and start containers",
		RunE: func(cmd *cobra.Command, args []string) error {
			composeProject, err := command.ProjectFromEnv()
			if err != nil {
				return err
			}

			err = composeProject.Up()
			if err != nil {
				return err
			}

			return nil
		},
	}

	return cmd
}

func downCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "down",
		Short: "Stop and remove containers",
		RunE: func(cmd *cobra.Command, args []string) error {
			composeProject, err := command.ProjectFromEnv()
			if err != nil {
				return err
			}

			err = composeProject.Down()
			if err != nil {
				return err
			}

			return nil
		},
	}

	return cmd
}