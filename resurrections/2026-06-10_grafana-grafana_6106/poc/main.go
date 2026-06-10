package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"math/rand"
	"time"
)

type DataPoint struct {
	Value    float64 `json:"value"`
	StdDev   float64 `json:"stdDev"`
	Samples  int     `json:"samples"`
}

type GraphData struct {
	DataPoints []DataPoint `json:"dataPoints"`
}

func calculateErrorBars(dataPoints []DataPoint) ([]float64, error) {
	if len(dataPoints) == 0 {
		return nil, errors.New("no data points")
	}

	errBars := make([]float64, len(dataPoints))
	for i, dp := range dataPoints {
		errBars[i] = dp.StdDev * math.Sqrt(float64(dp.Samples))
	}

	return errBars, nil
}

func generateRandomData() GraphData {
	rand.Seed(time.Now().UnixNano())
	dp := make([]DataPoint, 10)
	for i := range dp {
		dp[i].Value = rand.Float64() * 100
		dp[i].StdDev = rand.Float64() * 10
		dp[i].Samples = rand.Intn(100) + 1
	}

	return GraphData{DataPoints: dp}
}

func main() {
	data := generateRandomData()
	errBars, err := calculateErrorBars(data.DataPoints)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("Data Points:")
	for i, dp := range data.DataPoints {
		fmt.Printf("Value: %.2f, StdDev: %.2f, Samples: %d, Error Bar: %.2f\n", dp.Value, dp.StdDev, dp.Samples, errBars[i])
	}

	jsonData, _ := json.MarshalIndent(data, "", "\t")
	fmt.Println("\nJSON Data:\n", string(jsonData))
}