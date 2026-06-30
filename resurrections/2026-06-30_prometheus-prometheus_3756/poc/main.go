package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"strconv"
	"strings"
)

type ServiceDiscoveryConfig struct {
	Annotations map[string]string
}

type Port struct {
	Name string
	Port int
}

func parsePorts(annotation string) ([]Port, error) {
	var ports []Port
	if annotation == "" {
		return ports, nil
	}
	parts := strings.Split(annotation, ",")
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		var port Port
		err := json.Unmarshal([]byte(part), &port)
		if err != nil {
			// Try parsing as a simple port number
			portNumber, err := strconv.Atoi(part)
			if err != nil {
				return nil, errors.New("invalid port format: " + part)
			}
			port.Port = portNumber
		} else {
			if port.Name == "" || port.Port == 0 {
				return nil, errors.New("invalid port format: " + part)
			}
		}
		ports = append(ports, port)
	}
	return ports, nil
}

func main() {
	config := ServiceDiscoveryConfig{
		Annotations: map[string]string{
			"prometheus.io/port": "8080, 8081, {\"name\": \"http\", \"port\": 8082}",
		},
	}
	annotation, ok := config.Annotations["prometheus.io/port"]
	if !ok {
		log.Println("No port annotation found")
		return
	}
	ports, err := parsePorts(annotation)
	if err != nil {
		log.Printf("Error parsing ports: %v", err)
		return
	}
	for _, port := range ports {
		log.Printf("Scraping port: %d (%s)\n", port.Port, port.Name)
	}
}