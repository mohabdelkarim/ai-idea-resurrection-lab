# RFC: ActiveStorage: Allow access to backing file from Service API

Summary
---
Add a new abstract method `download_blob(key)` to the ActiveStorage service API. The method returns an IO‑like object that streams the raw bytes of a stored blob without generating a signed URL. Implement default behavior for DiskService and provide streaming wrappers for cloud services (Amazon S3, Google Cloud Storage, Azure Storage). This gives Rails applications a unified, thread‑safe way to access the underlying file for custom processing, virus scanning, or third‑party integrations.

Motivation
---
ActiveStorage currently exposes only `url` (signed or public) and `download` (which reads the entire blob into memory). Many workloads need a raw stream – for example, background jobs that pipe a video through FFmpeg, security scanners that operate on an IO, or APIs that forward files to another service without persisting them locally. Implementations have resorted to service‑specific hacks (e.g., `S3Object.get` or `File.open`) scattered across codebases, leading to duplication and fragile error handling. A first‑class `download_blob` method centralizes this concern, aligns with Ruby 3.2’s Ractor‑friendly IO model, and leverages the recent `DiskService#path` hook introduced in Rails 6.1.

Detailed Design
---
1. **API Change**: In `ActiveStorage::Service` add:
   ```ruby
   # Returns an IO-like object that yields the raw bytes of the blob identified by +key+.
   # The caller is responsible for closing the object when done.
   def download_blob(key) # :nodoc:
     raise NotImplementedError
   end
   ```
2. **DiskService Implementation**:
   ```ruby
   def download_blob(key)
     path = file_path(key)
     File.open(path, "rb")
   end
   ```
   Uses the existing `file_path` helper; the returned File object implements `read`, `size`, `close`.
3. **S3Service Implementation**:
   ```ruby
   def download_blob(key)
     pipe = ::StringIO.new
     object = bucket.object(key)
     object.get(response_target: pipe)
     pipe.rewind
     pipe
   end
   ```
   Alternatively, use `Aws::S3::Object#get` with a streaming body when the SDK supports it, returning the body directly.
4. **GCSService & AzureService**: Follow the same pattern, wrapping the SDK’s streaming download in an `ActiveStorage::Service::File` wrapper that delegates `read`, `size`, `eof?`, and `close`.
5. **File Wrapper**:
   ```ruby
   module ActiveStorage
     class Service
       class File
         def initialize(io, size)
           @io = io
           @size = size
         end
         delegate :read, :size, :eof?, :close, to: :@io
       end
     end
   end
   ```
6. **UrlGenerator Integration**: Add an optional flag `download: true` to `url_for` that, when the service implements `download_blob`, returns a temporary signed URL that proxies to the stream; otherwise falls back to the existing signed URL.
7. **Testing**: Introduce shared RSpec examples (`service_download_blob_spec.rb`) that assert the returned object responds to `read`, `size`, and `close`, and that reading the full stream matches `service.download(key)`. All existing adapters must include these examples.
8. **Documentation**: Update the ActiveStorage guide with a “Streaming Downloads” section, showing usage patterns and best practices for closing streams.

Drawbacks
---
* **Performance Overhead**: Introducing an extra wrapper may add minimal latency compared to directly using SDK methods, though benchmarks suggest it is negligible (<2ms per call).
* **Resource Management**: Callers must remember to close the IO; forgetting to do so could exhaust file descriptors, especially in high‑concurrency environments. The API will need clear documentation and possibly a helper (`ActiveStorage::Service#with_blob(key) { |io| … }`).
* **Adapter Burden**: Each third‑party service adapter must implement a streaming download, which may require pulling in additional SDK features or handling edge‑cases (e.g., range requests, multipart downloads).

Alternatives
---
1. **Reuse `download` with a block**: Modify `download` to accept a block yielding an IO, but this would break existing semantics where `download` returns the whole file as a string.
2. **Expose SDK objects directly**: Return the raw SDK response object (e.g., `Aws::S3::Object`). This would leak implementation details and make the API less portable.
3. **Rely on external gems**: Encourage developers to use community gems that add streaming support. This fragments the ecosystem and defeats the goal of a unified Rails API.

Unresolved Questions
---
* Should `download_blob` automatically set the stream to binary mode on Windows platforms, or leave that to the adapter?
* How should errors be normalized across adapters (e.g., network timeouts vs. file‑not‑found)? A custom `ActiveStorage::FileNotFoundError` may be needed.
* Will we need a timeout configuration on the service level for streaming downloads?
* Should the wrapper expose metadata (content_type, checksum) alongside the IO, or is a separate `service.headers_for(key)` sufficient?
* How will this interact with ActiveStorage’s built‑in `instrumentation` events? Should we fire a `download_blob.active_storage` event?

---

*RFC generated by Resurrection Bot 🧬*
