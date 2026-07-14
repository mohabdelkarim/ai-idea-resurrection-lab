package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"net/http"

	"github.com/grafana/grafana-sdk-go/grafana"
	"github.com/grafana/grafana-sdk-go/grafana/model"
)

type ErrorBar struct {
	Mean     float64 `json:"mean"`
	StdDev   float64 `json:"stdDev"`
	Interval float64 `json:"interval"`
}

type DataPoint struct {
	Value    float64 `json:"value"`
	ErrorBar ErrorBar `json:"errorBar"`
}

func calculateErrorInterval(stdDev, interval float64) float64 {
	return stdDev * interval
}

func processDataPoints(dataPoints []DataPoint) ([]DataPoint, error) {
	if len(dataPoints) == 0 {
		return nil, errors.New("no data points provided")
	}

	processedPoints := make([]DataPoint, 0)
	for _, point := range dataPoints {
		errorInterval := calculateErrorInterval(point.ErrorBar.StdDev, point.ErrorBar.Interval)
		point.ErrorBar.Interval = errorInterval
		processedPoints = append(processedPoints, point)
	}

	return processedPoints, nil
}

func renderGraph(dataPoints []DataPoint) error {
	// Simulate rendering graph with error bars
	for _, point := range dataPoints {
		fmt.Printf("Rendering point with value: %f, error bar: %+v\n", point.Value, point.ErrorBar)
	}

	return nil
}

func main() {
	dataPoints := []DataPoint{
		{Value: 10, ErrorBar: ErrorBar{Mean: 10, StdDev: 2, Interval: 1.96}},
		{Value: 20, ErrorBar: ErrorBar{Mean: 20, StdDev: 3, Interval: 1.96}},
	}

	processedPoints, err := processDataPoints(dataPoints)
	if err != nil {
		fmt.Println(err)
		return
	}

	err = renderGraph(processedPoints)
	if err != nil {
		fmt.Println(err)
		return
	}
}