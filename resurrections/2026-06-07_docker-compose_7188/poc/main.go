package main

import (
	"fmt"
	"log"
	"net"
	"strconv"
	"strings"
)

type PortRange struct {
	Start int
	End   int
}

func parsePortRange(portRangeStr string) (*PortRange, error) {
	parts := strings.Split(portRangeStr, "-")
	if len(parts) != 2 {
		return nil, fmt.Errorf("invalid port range: %s", portRangeStr)
	}
	start, err := strconv.Atoi(parts[0])
	if err != nil {
		return nil, err
	}
	end, err := strconv.Atoi(parts[1])
	if err != nil {
		return nil, err
	}
	if start > end {
		return nil, fmt.Errorf("invalid port range: %s", portRangeStr)
	}
	return &PortRange{Start: start, End: end}, nil
}

func isPortInRange(port int, portRange *PortRange) bool {
	return port >= portRange.Start && port <= portRange.End
}

func allocatePort(portRanges []*PortRange) (int, error) {
	// Simulate port allocation
	for port := 32768; port <= 61000; port++ {
		conflict := false
		for _, portRange := range portRanges {
			if isPortInRange(port, portRange) {
				conflict = true
				break
		}
		}
		if !conflict {
			return port, nil
		}
	}
	return 0, fmt.Errorf("no available ports")
}

func main() {
	portRanges := make([]*PortRange, 0)
	services := map[string]string{
		"postgres-foo": "32768-61000",
		"postgres-bar": "32768-61000",
	}
	for service, portRangeStr := range services {
		log.Printf("Service %s: %s\n", service, portRangeStr)
		portRange, err := parsePortRange(portRangeStr)
		if err != nil {
			log.Printf("Error parsing port range for service %s: %v\n", service, err)
			continue
		}
		portRanges = append(portRanges, portRange)
	}
	allocatedPort, err := allocatePort(portRanges)
	if err != nil {
		log.Printf("Error allocating port: %v\n", err)
	} else {
		log.Printf("Allocated port: %d\n", allocatedPort)
	}
	// Test port allocation
	tcpAddr, err := net.ResolveTCPAddr("tcp", "127.0.0.1:"+strconv.Itoa(allocatedPort))
	if err != nil {
		log.Println(err)
		return
	}
	conn, err := net.DialTCP("tcp", nil, tcpAddr)
	if err != nil {
		log.Println(err)
		return
	}
	defer conn.Close()
	log.Println("Port is available")
}