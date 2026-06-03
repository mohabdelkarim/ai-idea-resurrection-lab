package main

import (
	"fmt"
	"math"
	"github.com/robfig/cron/v3"
	"golang.org/x/sync"
	"time"
)

type HorizontalPodAutoscaler struct {
	minReplicas int
	maxReplicas int
	currentReplicas int
	targetCPUUtilizationPercentage float64
	currentCPUUtilizationPercentage float64
}

func (h *HorizontalPodAutoscaler) ScaleDown() {
	if h.currentReplicas > h.minReplicas && h.currentCPUUtilizationPercentage < h.targetCPUUtilizationPercentage {
		h.currentReplicas--
		fmt.Println("Scaled down to", h.currentReplicas, "replicas")
	}
}

func (h *HorizontalPodAutoscaler) ScaleUp() {
	if h.currentReplicas < h.maxReplicas && h.currentCPUUtilizationPercentage > h.targetCPUUtilizationPercentage {
		h.currentReplicas++
		fmt.Println("Scaled up to", h.currentReplicas, "replicas")
	}
}

func (h *HorizontalPodAutoscaler) Run() {
	// Simulate metrics collection
	go func() {
		for {
			h.currentCPUUtilizationPercentage = 0 // Simulate low CPU usage
			h.ScaleDown()
			h.ScaleUp()
			time.Sleep(10 * time.Second)
		}
	}()

	// Start a cron job to check scaling every 10 seconds
	c := cron.New()
	err := c.AddFunc("*/10 * * * * *", func() {
		h.ScaleDown()
		h.ScaleUp()
	})
	if err != nil {
		fmt.Println(err)
	}
	c.Start()

	select {}
}

func main() {
	hpa := &HorizontalPodAutoscaler{
	minReplicas: 2,
	maxReplicas: 4,
	currentReplicas: 4,
	targetCPUUtilizationPercentage: 40,
	currentCPUUtilizationPercentage: 0,
	}
	hpa.Run()
}