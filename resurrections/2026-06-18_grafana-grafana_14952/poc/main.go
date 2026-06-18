package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

type SignalConfig struct {
	APIKey    string `json:"api_key"`
	Number    string `json:"number"`
	Recipient string `json:"recipient"`
}

type SignalMessage struct {
	Message string `json:"message"`
}

func sendSignalMessage(config SignalConfig, message string) error {
	// Prepare Signal API request
	requestBody := SignalMessage{
	Message: message,
	}
	body, err := json.Marshal(requestBody)
	if err != nil {
		return err
	}
	request, err := http.NewRequest("POST", "https://api.signal.org/v1/messages", bytes.NewBuffer(body))
	if err != nil {
		return err
	}
	request.Header.Set("Authorization", fmt.Sprintf("Bearer %s", config.APIKey))
	request.Header.Set("Content-Type", "application/json")

	response, err := http.DefaultClient.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()

	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("Signal API returned status code %d", response.StatusCode)
	}

	return nil
}

func main() {
	// Example usage
	config := SignalConfig{
	APIKey:    "your_signal_api_key",
	Number:    "your_signal_number",
	Recipient: "your_recipient",
	}

	message := "This is a test message from Grafana"
	err := sendSignalMessage(config, message)
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println("Message sent successfully")
	}
}