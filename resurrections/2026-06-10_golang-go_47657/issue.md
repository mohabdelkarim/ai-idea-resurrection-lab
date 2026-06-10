# proposal: sync, sync/atomic: add PoolOf, MapOf, ValueOf

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#47657](https://github.com/golang/go/issues/47657)
**Reactions:** 171 👍
**Created:** 2021-08-11T21:53:13Z
**Last Activity:** 2026-01-01T04:48:54Z
**Labels:** Proposal, FrozenDueToAge, Proposal-Hold, generics

---

## Original Description

This proposal is for use with #43651.  We propose using type parameters to add compile-time-type-safe variants of `sync.Pool`, `sync.Map`, and `atomic.Value`.

This proposal is not targeted for any specific Go release.

```Go
package sync

// A PoolOf is a set of temporary objects of type T that may be individually saved and retrieved.
// ...and so forth
type PoolOf[T any] struct {
    ...
    New func() T
}

// Put adds x to the pool.
func (p *PoolOf[T]) Put(x T)

// Get selects an arbitrary item from the Pool, removes it from the
// Pool, and returns it to the caller.
// The bool result reports whether a value was found.
// ...and so forth
//
// If Get would otherwise return the second result as false and p.New is non-nil,
// Get returns the result of calling p.New and true.
func (p *PoolOf[T]) Get() (T, bool)

// MapOf is like a Go map[K]V but is safe for concurrent use
// by multiple goroutines without additional locking or coordination.
// ...and so forth
type MapOf[K comparable, V any] struct { ... }

// Load returns the value stored in the map for a key, or the zero value if no
// value is present.
// The ok result indicates whether value was found in the map.
func (m *MapOf[K, V]) Load(key K) (value V, ok bool)

// Store sets the value for a key.
func (m *MapOf[K, V]) Store(key K, value V)

// LoadOrStore returns the existing value for the key if present.
// Otherwise, it stores and returns the given value.
// The loaded result is true if the value was loaded, false if stored.
func (m *MapOf[K, V]) LoadOrStore(key K, value V) (actual V, loaded bool)

// LoadAndDelete deletes the value for a key, returning the previous value if any.
// The loaded result reports whether the key was present.
func (m *MapOf[K, V]) LoadAndDelete(key K) (value V, loaded bool)

// Delete deletes the value for a key.
func (m *MapOf[K, V]) Delete(key K)

// Range calls f sequentially for each key and value present in the map.
// ... and so forth
func (m *MapOf[K, V]) Range(f func(key K, value V) bool)
```

```Go
package atomic

// A ValueOf provides an atomic load and store of a value of a given type.
// The zero value for a Value returns the zero value of the type from Load.
// Once Store has been called, a Value must not be copied.
//
// A Value must not be copied after first use.
type ValueOf[T any] struct { ... }

// Load returns the value set by the most recent Store.
// It returns the zero value of T if there has been no call to Store for this Value.
func (v *ValueOf[T]) Load() (val T)

// Store sets the value of the Value to x.
func (v *ValueOf[T]) Store(val T)

// Swap stores new into Value and returns the previous value. It returns the zero value
// if the Value is empty.
func (v *ValueOf[T]) Swap(new T) (old T)

// Note: no CompareAndSwap method; it would require a comparable T.
```

---

*Resurrected by Resurrection Bot 🧬*
