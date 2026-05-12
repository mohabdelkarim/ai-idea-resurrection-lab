package main

import (
	"errors"
	"fmt"
)

// A simple function to demonstrate error handling
func divide(x, y float64) (float64, error) {
	if y == 0 {
		return 0, errors.New("division by zero")
	}
	return x / y, nil
}

// A function to handle errors in a centralized way
func handleError(err error) {
	if err != nil {
		fmt.Println("Error occurred:", err)
		// You can add more error handling logic here
	}
}

// A function to demonstrate the usage of 'if err != nil'
func calculate(x, y float64) {
	result, err := divide(x, y)
	if err != nil {
		handleError(err)
		return
	}
	fmt.Println("Result:", result)
}

// A function to demonstrate error wrapping and unwrapping
func wrapError(err error) error {
	return fmt.Errorf("wrapped error: %w", err)
}

// A function to demonstrate error wrapping and unwrapping
func unwrapError(err error) {
	if err != nil {
		fmt.Println("Unwrapped error:", errors.Unwrap(err))
	}
}

func main() {
	// Test the divide function
	result, err := divide(10, 2)
	if err != nil {
		handleError(err)
	} else {
		fmt.Println("Result:", result)
	}

	// Test the calculate function
	calculate(10, 2)
	calculate(10, 0)

	// Test error wrapping and unwrapping
	err := errors.New("original error")
	wrappedErr := wrapError(err)
	unwrapError(wrappedErr)

	// Test the handleError function
	handleError(nil)
	handleError(errors.New("test error"))
}