package main

import (
	"fmt"
	"log"
	"os"
	"os/user"
	"strconv"
)

func main() {
	// Get the current user and group IDs
	u, err := user.Current()
	if err != nil {
		log.Fatalf("Failed to get current user: %v", err)
	}

	userID, err := strconv.Atoi(u.Uid)
	if err != nil {
		log.Fatalf("Failed to convert user ID to integer: %v", err)
	}

	groupID, err := strconv.Atoi(u.Gid)
	if err != nil {
		log.Fatalf("Failed to convert group ID to integer: %v", err)
	}

	// Set the COMPOSE_USER_ID and COMPOSE_GROUP_ID environment variables
	err = os.Setenv("COMPOSE_USER_ID", strconv.Itoa(userID))
	if err != nil {
		log.Fatalf("Failed to set COMPOSE_USER_ID environment variable: %v", err)
	}

terr := os.Setenv("COMPOSE_GROUP_ID", strconv.Itoa(groupID))
	if terr != nil {
		log.Fatalf("Failed to set COMPOSE_GROUP_ID environment variable: %v", terr)
	}

	// Print the set environment variables for verification
	fmt.Println("COMPOSE_USER_ID=", os.Getenv("COMPOSE_USER_ID"))
	fmt.Println("COMPOSE_GROUP_ID=", os.Getenv("COMPOSE_GROUP_ID"))
}