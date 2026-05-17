package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"os/user"
	"strconv"
)

func main() {
	// Get the current user and group IDs
	err := run()
	if err != nil {
		log.Fatal(err)
	}
}

func run() error {
	// Get the current user
	currentUser, err := user.Current()
	if err != nil {
		return err
	}

	// Get the user ID
	userID, err := strconv.Atoi(currentUser.Uid)
	if err != nil {
		return err
	}

	// Get the group ID
	groupID, err := strconv.Atoi(currentUser.Gid)
	if err != nil {
		return err
	}

	// Set environment variables
	err = os.Setenv("COMPOSE_USER_ID", currentUser.Uid)
	if err != nil {
		return err
	}

	err = os.Setenv("COMPOSE_GROUP_ID", currentUser.Gid)
	if err != nil {
		return err
	}

	// Print the environment variables for testing
	fmt.Println("COMPOSE_USER_ID=", os.Getenv("COMPOSE_USER_ID"))
	fmt.Println("COMPOSE_GROUP_ID=", os.Getenv("COMPOSE_GROUP_ID"))

	return nil
}