package main

import (
	"fmt"
	"sync"
)

// Lazy represents a value that may or may not have been computed.
type Lazy[T any] struct {
	mu       sync.Mutex
	computed bool
	value    T
	fn       func() T
}

// NewLazy returns a new lazy value.
func NewLazy[T any](fn func() T) *Lazy[T] {
	return &Lazy[T]{
		fn: fn,
	}
}

// Value returns the computed value.
func (l *Lazy[T]) Value() T {
	l.mu.Lock()
	defer l.mu.Unlock()
	if !l.computed {
		l.value = l.fn()
		l.computed = true
	}
	return l.value
}

// IsEvaluated returns true if the value has been computed.
func (l *Lazy[T]) IsEvaluated() bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.computed
}

func main() {
	// Create a new lazy value that computes the result of an expensive operation.
	expensiveOperation := func() int {
		// Simulate an expensive operation.
		fmt.Println("Computing expensive operation...")
		return 42
	}

	lazyValue := NewLazy(expensiveOperation)

	// The value has not been computed yet.
	fmt.Println("Value has been computed:", lazyValue.IsEvaluated())

	// Compute the value.
	value := lazyValue.Value()
	fmt.Println("Value:", value)

	// The value has been computed.
	fmt.Println("Value has been computed:", lazyValue.IsEvaluated())

	// Try to compute the value again.
	valueAgain := lazyValue.Value()
	fmt.Println("Value (again):", valueAgain)

	if value != valueAgain {
		fmt.Println("Error: computed values do not match")
	}

	// Create a new lazy value that returns an error.
	errorOperation := func() (int, error) {
		return 0, fmt.Errorf("something went wrong")
	}

	lazyValueWithError := NewLazy(func() int {
		v, err := errorOperation()
		if err != nil {
			panic(err)
		}
		return v
	})

	// Compute the value.
	valueWithError := lazyValueWithError.Value()
	fmt.Println("Value with error:", valueWithError)
}