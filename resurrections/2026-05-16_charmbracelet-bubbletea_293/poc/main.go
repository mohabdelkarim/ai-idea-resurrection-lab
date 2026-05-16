package main

import (
	"bufio"
	"bytes"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"strings"
)

const (
	CSI = "\x1b["
	OSC = "\x1b]"
	BEL = "\a"
	ST = "\x1b\\"
)

type CSIuInputHandler struct {
	state string
}

func NewCSIuInputHandler() *CSIuInputHandler {
	return &CSIuInputHandler{state: "idle"}
}

func (h *CSIuInputHandler) HandleInput(input string) (string, error) {
	switch h.state {
	case "idle":
		if strings.HasPrefix(input, CSI) {
			h.state = "csi"
			return h.handleCSI(input)
		}
	case "csi":
		return h.handleCSI(input)
	default:
		err := errors.New("invalid state")
		h.state = "idle"
		return "", err
	}
}

func (h *CSIuInputHandler) handleCSI(input string) (string, error) {
	if !strings.HasPrefix(input, CSI) {
		err := errors.New("invalid CSI sequence")
		h.state = "idle"
		return "", err
	}
	input = strings.TrimPrefix(input, CSI)
	parts := strings.SplitN(input, " ", 2)
	if len(parts) < 2 {
		err := errors.New("invalid CSI sequence")
		h.state = "idle"
		return "", err
	}
	code, err := strconv.Atoi(parts[0])
	if err != nil {
		h.state = "idle"
		return "", err
	}
	switch code {
	case 1: // Keyboard report
		return h.handleKeyboardReport(parts[1])
	default:
		err := fmt.Errorf("unsupported CSI code: %d", code)
		h.state = "idle"
		return "", err
	}
}

func (h *CSIuInputHandler) handleKeyboardReport(report string) (string, error) {
	report = strings.TrimSuffix(report, "m")
	bytes, err := hex.DecodeString(report)
	if err != nil {
		h.state = "idle"
		return "", err
	}
	// Process keyboard report bytes
	return string(bytes), nil
}

func main() {
	handler := NewCSIuInputHandler()
	err := bufio.NewReader(os.Stdin).ReadString('\n')
	if err != nil {
		fmt.Println(err)
		return
	}
	input := strings.TrimSuffix(err.Error(), "\n")
	output, err := handler.HandleInput(input)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(output)
}