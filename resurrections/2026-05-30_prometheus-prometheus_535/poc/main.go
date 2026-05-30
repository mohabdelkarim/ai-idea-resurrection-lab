package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"time"

	"github.com/prometheus/client_golang/api"
	"github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/common/model"
)

func main() {
	if len(os.Args) != 3 {
		log.Fatal("Usage: ", os.Args[0], " <prometheus_url> <input_file>")
	}

	prometheusURL := os.Args[1]
	inputFile := os.Args[2]

	// Create a new Prometheus API client
	rsp, err := api.NewClient(api.Config{
		Address: prometheusURL,
	})
	if err != nil {
		log.Fatal(err)
	}
	v1Client := v1.NewAPIClient(rsp)

	// Read the input file
	data, err := os.ReadFile(inputFile)
	if err != nil {
		log.Fatal(err)
	}

	// Unmarshal the input data
	var inputData []model.Sample
	if err := json.Unmarshal(data, &inputData); err != nil {
		log.Fatal(err)
	}

	// Create a new write API request
	req := v1.NewWriteRequest(time.Now())
	for _, sample := range inputData {
		err := req.AddSample(sample)
		if err != nil {
			log.Fatal(err)
		}
	}

	// Send the write request
	err = v1Client.Write(context.Background(), req)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Bulk import successful")
}

func (c *v1APIClient) Write(ctx context.Context, req *v1.WriteRequest) error {
	// Implement the write API request
	// This is a simplified example and may need to be adapted to your specific use case
	buf, err := req.MarshalJSON()
	if err != nil {
		return err
	}

	resp, err := c.client.Do(ctx, "POST", "/api/v1/write", buf)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	return nil
}