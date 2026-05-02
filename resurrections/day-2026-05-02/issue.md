# Protobuf seems like a lot of overhead for this use case?

**Repository:** [denoland/deno](https://github.com/denoland/deno)
**Issue:** [denoland/deno#269](https://github.com/denoland/deno/issues/269)
**Reactions:** 113 👍
**Created:** 2018-06-19T04:26:53Z
**Last Activity:** 2018-08-03T02:00:23Z
**Labels:** 

---

## Original Description

Hello. I'm the guy who wrote Protobuf v2 and open sourced it at Google. (I also, just in the last year, built Cloudflare Workers, a non-Node JavaScript server runtime embedding V8, with a focus on secure sandboxing and high multi-tenancy.)

I was surprised by the choice of Protobuf for intra-process communications within Deno. Protobuf's backwards compatibility guarantees and compact wire representation offer no benefit here, while the serialize/parse round-trip on every I/O seems like it would be pretty expensive.

I suppose the main motivation for using Protobuf here is to get convenient code for transmitting data that is compatible across languages?

Have you considered Cap'n Proto for this? I created Cap'n Proto shortly after leaving Google. It works a lot like Protobuf, except that the generated getters and setters operate directly on a backing byte array (e.g. ArrayBuffer in JavaScript), using a C-struct-like layout. Since you can directly share that byte array between code in different languages, you can construct a message in one language and then consume it in another without even making a copy in between, much less a serialize/parse round trip. Communication between a sandbox and a supervisor was in fact a motivating use case for Cap'n Proto.

Cap'n Proto is well-supported in C++, Rust, and Go. There is also [a mostly-complete TypeScript implementation](https://github.com/jdiaz5513/capnp-ts). Admittedly the TypeScript implementation has not received a whole lot of real-world usage, but there's interest I may be willing to directly adopt and support it for you. (I expect to need it in my own work soon anyway.)

---

*Resurrected by Resurrection Bot 🧬*
