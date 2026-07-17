# Feature Request: Add MTP / speculative decoding support to llama-bench for PR #22673

**Repository:** [ggerganov/llama.cpp](https://github.com/ggml-org/llama.cpp)
**Issue:** [ggerganov/llama.cpp#22947](https://github.com/ggml-org/llama.cpp/issues/22947)
**Reactions:** 16 👍
**Created:** 2026-05-11T16:06:00Z
**Last Activity:** 2026-07-14T01:09:58Z
**Labels:** enhancement, stale

---

## Original Description

### Prerequisites

- [x] I am running the latest code. Mention the version if possible as well.
- [x] I carefully followed the [README.md](https://github.com/ggml-org/llama.cpp/blob/master/README.md).
- [x] I searched using keywords relevant to my issue to make sure that I am creating a new issue that is not already open (or closed).
- [x] I reviewed the [Discussions](https://github.com/ggml-org/llama.cpp/discussions), and have a new and useful enhancement to share.

### Feature Description

The draft MTP PR  #22673  adds speculative decoding / MTP support to:

llama-cli
llama-server

using flags such as:
`--spec-type mtp`
`--spec-draft-n-max 3`
`--spec-draft-ngl 99`

These flags work correctly in:

`llama-cli`
`llama-server` 

(have only tested on these two)

but are unrecognized in `llama-bench`
Example:

```
./build/bin/llama-bench \
  -m model.gguf \
  --spec-type mtp
 -- spec-draft-n-max 3,4,5
 -- spec-draft-ngl 99,100
```
returns:

> error: invalid parameter for argument: --spec-type

### Motivation

Currently MTP benchmarking requires custom scripts or `llama-server` setups since speculative decoding flags are unavailable in `llama-bench`.

Adding support directly to `llama-bench` would make it much easier for users to quickly test and compare speculative decoding configurations such as different `n-max` values, context depths, throughput scaling, and VRAM tradeoffs using the built-in benchmarking tooling.


### Possible Implementation

I did some digging and it looks like llama-bench currently uses its own parser / benchmark loop instead of the shared common argument infrastructure used by `llama-cli` and `llama-server`, which is likely why the speculative decoding flags are currently unavailable there.

---

*Resurrected by Resurrection Bot 🧬*
