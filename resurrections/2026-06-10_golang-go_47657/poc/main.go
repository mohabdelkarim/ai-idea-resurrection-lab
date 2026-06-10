package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

// PoolOf is a set of temporary objects of type T that may be individually saved and retrieved.
type PoolOf[T any] struct {
	mu    sync.Mutex
	objs  []T
	New   func() T
}

// Put adds x to the pool.
func (p *PoolOf[T]) Put(x T) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.objs = append(p.objs, x)
}

// Get selects an arbitrary item from the Pool, removes it from the
// Pool, and returns it to the caller.
// The bool result reports whether a value was found.
func (p *PoolOf[T]) Get() (T, bool) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if len(p.objs) == 0 {
		if p.New != nil {
			return p.New(), true
		}
		var zero T
		return zero, false
	}
	obj := p.objs[len(p.objs)-1]
	p.objs = p.objs[:len(p.objs)-1]
	return obj, true
}

// MapOf is like a Go map[K]V but is safe for concurrent use
// by multiple goroutines without additional locking or coordination.
type MapOf[K comparable, V any] struct {
	mu    sync.RWMutex
	m     map[K]V
}

// Load returns the value stored in the map for a key, or the zero value if no
// value is present.
// The ok result indicates whether value was found in the map.
func (m *MapOf[K, V]) Load(key K) (value V, ok bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	value, ok = m.m[key]
	return
}

// Store sets the value for a key.
func (m *MapOf[K, V]) Store(key K, value V) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.m == nil {
		m.m = make(map[K]V)
	}
	m.m[key] = value
}

// LoadOrStore returns the existing value for the key if present.
// Otherwise, it stores and returns the given value.
// The loaded result is true if the value was loaded, false if stored.
func (m *MapOf[K, V]) LoadOrStore(key K, value V) (actual V, loaded bool) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.m == nil {
		m.m = make(map[K]V)
	}
	actual, loaded = m.m[key]
	if !loaded {
		m.m[key] = value
	}
	return
}

// LoadAndDelete deletes the value for a key, returning the previous value if any.
// The loaded result reports whether the key was present.
func (m *MapOf[K, V]) LoadAndDelete(key K) (value V, loaded bool) {
	m.mu.Lock()
	defer m.mu.Unlock()
	value, loaded = m.m[key]
	if loaded {
		delete(m.m, key)
	}
	return
}

// Delete deletes the value for a key.
func (m *MapOf[K, V]) Delete(key K) {
	m.mu.Lock()
	defer m.mu.Unlock()
	delete(m.m, key)
}

// Range calls f sequentially for each key and value present in the map.
func (m *MapOf[K, V]) Range(f func(key K, value V) bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	for key, value := range m.m {
		if !f(key, value) {
			break
		}
	}
}

// ValueOf provides an atomic load and store of a value of a given type.
type ValueOf[T any] struct {
	val atomic.Pointer[T]
}

// Load returns the value set by the most recent Store.
// It returns the zero value of T if there has been no call to Store for this Value.
func (v *ValueOf[T]) Load() (val T) {
	p := v.val.Load()
	if p == nil {
		var zero T
		return zero
	}
	return *p
}

// Store sets the value of the Value to x.
func (v *ValueOf[T]) Store(val T) {
	v.val.Store(&val)
}

// Swap stores new into Value and returns the previous value. It returns the zero value
// if the Value is empty.
func (v *ValueOf[T]) Swap(new T) (old T) {
	oldP := v.val.Swap(&new)
	if oldP == nil {
		var zero T
		return zero
	}
	return *oldP
}

func main() {
	// Test PoolOf
	pool := &PoolOf[int]{New: func() int { return 42 }}
	pool.Put(1)
	pool.Put(2)
	val, ok := pool.Get()
	fmt.Println(val, ok) // prints: 2 true

	// Test MapOf
	m := &MapOf[string, int]{}
	m.Store("a", 1)
	m.Store("b", 2)
	val, ok = m.Load("a")
	fmt.Println(val, ok) // prints: 1 true
	val, ok = m.LoadOrStore("c", 3)
	fmt.Println(val, ok) // prints: 0 false

	// Test ValueOf
	v := &ValueOf[int]{}
	v.Store(42)
	val = v.Load()
	fmt.Println(val) // prints: 42
	old := v.Swap(24)
	fmt.Println(old) // prints: 42
}