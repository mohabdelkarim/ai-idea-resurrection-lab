# RFC: Implement Expire on hash

1. Summary
Add per-field expiration to Redis hashes. Introduce a new internal representation for hash fields that includes an optional absolute expiration timestamp, new commands HSETEX and HEXPIRE, and integrate the feature with the existing lazy expiration and persistence mechanisms. The change is fully backward compatible: existing hash operations continue to work unchanged for fields without TTL.

2. Motivation
Redis hashes are widely used to store objects with many attributes. Currently the only way to expire data is at the key level, which forces developers to split logical objects across multiple keys or implement application‑side cleanup. Per‑field TTL would enable:
- Fine‑grained cache invalidation for individual attributes.
- Reduced memory pressure by automatically evicting stale fields.
- Simpler application code and fewer round‑trips (no need for separate cleanup scripts).
The original proposal stalled because the core dict could not store per‑field metadata without a major rewrite. Since Redis 7.0 the server now supports custom data types, background timers, and a generalized lazy expiration path, making a field‑level TTL feasible without invasive changes.

3. Detailed Design
a) Data Structure
   - Define `typedef struct {
        robj *value;            // existing field value
        mstime_t expire;        // 0 if no TTL, otherwise absolute Unix ms
     } HashFieldMeta;`
   - Replace the dict value type for hash objects from `robj*` to `HashFieldMeta*`. The dict key remains the field name string.

b) Command Set
   - `HSETEX key field ttl_ms value` – sets the field with a TTL (in milliseconds). Internally creates a `HashFieldMeta` with `expire = mstime()+ttl_ms`.
   - `HEXPIRE key field ttl_ms` – updates the TTL of an existing field; returns 1 if field exists, 0 otherwise.
   - Existing `HGET`, `HDEL`, `HGETALL`, etc., are modified to first invoke `hashFieldCheckExpire(fieldMeta)` which lazily deletes the field if `expire && expire <= mstime()`.

c) Expiration Engine
   - Reuse the server's lazy expiration hook: each hash field access triggers a check.
   - Add a periodic background timer (default every 100ms) that iterates over all hash objects with at least one expiring field (tracked via a global list `hashes_with_ttl`). The timer removes expired fields and updates memory usage counters.

d) Persistence
   - RDB: Extend `rdbSaveHashObject` to write an extra 8‑byte expiration timestamp after each field value when `expire != 0`. The format flag `RDB_TYPE_HASH_FIELD_META` distinguishes the new layout.
   - AOF: Append `HSETEX` commands for fields that have a TTL at the time of write. During rewrite, fields without TTL are saved as regular `HSET`.

e) Module API
   - Provide `RedisModule_CreateHashFieldMeta`, `RedisModule_HashFieldSetTTL`, and `RedisModule_HashFieldGetTTL` for module developers to implement identical semantics on custom data types.

f) Compatibility & Migration
   - Existing hashes are automatically upgraded on first write of a TTL field; a migration flag ensures that on‑disk data without TTL is loaded as `expire = 0`.
   - No change to the wire protocol for commands that do not involve TTL.

4. Drawbacks
   - Increased memory overhead: each field now stores an extra 8‑byte timestamp and a pointer to the meta struct, roughly +12‑16 bytes per field.
   - Slight CPU overhead on every hash field access due to the expiration check.
   - Background timer adds periodic work proportional to the number of hashes containing TTL fields; in pathological cases this could affect latency.
   - RDB/AOF files become larger for hashes with many expiring fields, potentially impacting replication bandwidth.

5. Alternatives
   a) Store per‑field TTL in a separate auxiliary key (e.g., a sorted set) and modify commands to consult it. This avoids changing the hash internals but adds extra key lookups and complicates atomicity.
   b) Implement expiration entirely in a Redis Module, exposing a new data type `hashex`. This would keep core unchanged but would require users to migrate data and lose built‑in hash commands.
   c) Reject the feature and continue to rely on key‑level TTL combined with application‑side cleanup. This retains simplicity but does not solve the identified use‑cases.

6. Unresolved Questions
   - What is the optimal frequency for the background TTL timer to balance latency and cleanup latency? Should it be configurable per‑instance?
   - How should replication handle a scenario where a replica evicts a field earlier than the master due to timing differences? Do we need a deterministic ordering guarantee?
   - Should we expose a `HTTL` command to query remaining TTL for a field, mirroring the existing `TTL` for keys?
   - Is there a need for a bulk expiration command (e.g., `HEXPIREALL`) for use‑cases like session invalidation?
   - Impact on cluster slot migration: ensure that field‑level TTL metadata moves correctly with hash slots.

---

*RFC generated by Resurrection Bot 🧬*
