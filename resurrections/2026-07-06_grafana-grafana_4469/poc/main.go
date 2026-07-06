package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"math"
)

type Panel struct {
	ID       string  `json:"id"`
	YAxisWidth float64 `json:"yAxisWidth"`
}

type Graph struct {
	Panels []Panel `json:"panels"`
}

func AlignYAxisWidths(graph *Graph) error {
	if graph == nil {
		return errors.New("graph is nil")
	}

	maxYAxisWidth := 0.0

	// Find the maximum Y-axis width across all panels
	for _, panel := range graph.Panels {
		if panel.YAxisWidth > maxYAxisWidth {
			maxYAxisWidth = panel.YAxisWidth
		}
	}

	// Update each panel's Y-axis width to the maximum width
	for i := range graph.Panels {
		graph.Panels[i].YAxisWidth = maxYAxisWidth
	}

	return nil
}

func main() {
	graph := &Graph{
		Panels: []Panel{
			{ID: "panel1", YAxisWidth: 50.0},
			{ID: "panel2", YAxisWidth: 75.0},
			{ID: "panel3", YAxisWidth: 30.0},
		},
	}

	err := AlignYAxisWidths(graph)
	if err != nil {
		log.Fatal(err)
	}

	buf, err := json.MarshalIndent(graph, "", "\t")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(buf))
}