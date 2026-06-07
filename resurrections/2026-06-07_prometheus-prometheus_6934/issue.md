# Memory usage spikes during WAL replay to more than normal usage

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#6934](https://github.com/prometheus/prometheus/issues/6934)
**Reactions:** 119 👍
**Created:** 2020-03-05T14:24:15Z
**Last Activity:** 2025-07-29T12:12:18Z
**Labels:** kind/bug, component/tsdb

---

## Original Description

**What did you do?**
Tried to start prometheus.

**What did you expect to see?**
Prometheus up & running, web interface showing up.

**What did you see instead? Under which circumstances?**
Prometheus runs out of RAM during "WAL segment loaded" process.

**Environment**
`Debian 9`

* System information:
`Linux 4.9.0-11-amd64 x86_64`

* Prometheus version:
```
prometheus, version 2.16.0 (branch: HEAD, revision: b90be6f32a33c03163d700e1452b54454ddce0ec)
  build user:       root@7ea0ae865f12
  build date:       20200213-23:50:02
  go version:       go1.13.8
```

* Prometheus configuration file:
```
global:
  evaluation_interval: 60s
  scrape_interval: 60s
...
...
...
```

* Logs:

This is what happends during the start after 10+- minutes:
```
... prometheus[39101]: level=info ts=2020-03-05T14:02:26.811Z caller=head.go:625 component=tsdb msg="WAL segment loaded" segment=41869 maxSegment=41871
... prometheus[39101]: level=info ts=2020-03-05T14:02:26.812Z caller=head.go:625 component=tsdb msg="WAL segment loaded" segment=41870 maxSegment=41871
... prometheus[39101]: level=info ts=2020-03-05T14:02:26.812Z caller=head.go:625 component=tsdb msg="WAL segment loaded" segment=41871 maxSegment=41871
... prometheus[39101]: fatal error: runtime: out of memory
... prometheus[39101]: runtime stack:
... prometheus[39101]: runtime.throw(0x253885d, 0x16)
... prometheus[39101]:         /usr/local/go/src/runtime/panic.go:774 +0x72
... prometheus[39101]: runtime.sysMap(0xce78000000, 0x14000000, 0x3f5bc78)
... prometheus[39101]:         /usr/local/go/src/runtime/mem_linux.go:169 +0xc5
... prometheus[39101]: runtime.(*mheap).sysAlloc(0x3f432c0, 0x11de6000, 0xc000, 0x4373e7)
... prometheus[39101]:         /usr/local/go/src/runtime/malloc.go:701 +0x1cd
... prometheus[39101]: runtime.(*mheap).grow(0x3f432c0, 0x8ef3, 0xffffffff)
... prometheus[39101]:         /usr/local/go/src/runtime/mheap.go:1255 +0xa3
... prometheus[39101]: runtime.(*mheap).allocSpanLocked(0x3f432c0, 0x8ef3, 0x3f5bc88, 0x20339d00000000)
... prometheus[39101]:         /usr/local/go/src/runtime/mheap.go:1170 +0x266
... prometheus[39101]: runtime.(*mheap).alloc_m(0x3f432c0, 0x8ef3, 0x101, 0x7f5861cc3fff)
... prometheus[39101]:         /usr/local/go/src/runtime/mheap.go:1022 +0xc2
... prometheus[39101]: runtime.(*mheap).alloc.func1()
... prometheus[39101]:         /usr/local/go/src/runtime/mheap.go:1093 +0x4c
... prometheus[39101]: runtime.(*mheap).alloc(0x3f432c0, 0x8ef3, 0x7f5861010101, 0x7f5861d11008)
... prometheus[39101]:         /usr/local/go/src/runtime/mheap.go:1092 +0x8a
... prometheus[39101]: runtime.largeAlloc(0x11de5ec0, 0x450101, 0x7f5861d11008)
... prometheus[39101]:         /usr/local/go/src/runtime/malloc.go:1138 +0x97
... prometheus[39101]: runtime.mallocgc.func1()
... prometheus[39101]:         /usr/local/go/src/runtime/malloc.go:1033 +0x46
... prometheus[39101]: runtime.systemstack(0x0)
... prometheus[39101]:         /usr/local/

---

*Resurrected by Resurrection Bot 🧬*
