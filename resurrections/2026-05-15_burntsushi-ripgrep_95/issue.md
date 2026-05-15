# fulltext search

**Repository:** [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
**Issue:** [BurntSushi/ripgrep#95](https://github.com/BurntSushi/ripgrep/issues/95)
**Reactions:** 17 👍
**Created:** 2016-09-26T00:19:35Z
**Last Activity:** 2021-02-01T22:52:15Z
**Labels:** enhancement

---

## Original Description

One of the things I've wanted `ripgrep` to do from before I even started writing it was fulltext search. General fulltext search is hard, but I wonder how far we can get by focusing on fulltext search _for code_.

I know there are some tools out there already that aspire to do this:
- [CodeSearch](https://github.com/google/codesearch), which is based on Russ Cox's excellent [trigram index](https://swtch.com/~rsc/regexp/regexp4.html) article.
- [Hound](https://github.com/etsy/hound) (which is also based on Cox's write up).

I'd like to start collecting use cases for functionality like this. In particular, most of the technical problems are already solved. Obviously, we have `ripgrep` and we have a lighting fast [data structure for representing an inverted index](https://github.com/BurntSushi/fst) already (indeed, it's the same as what Lucene uses internally). I think the key problems remaining are figuring out the user interaction story. Some things off the top of my head:
- Does such a tool belong in `ripgrep`? Can use of an index be done seamlessly while still being a top notch general purpose search tool?
- What specific things does it do that make _code_ search in particular better? Do we need parsers for every language?
- How is an out-of-band index maintained? Does a user need to manually update? Is it a daemon that watches directories for file notification and update itself automatically? How do we know if an index is out-of-date?

Anyway, I'd like to start thinking about this. I don't know when I'll start on an implementation, but it'd be good to get ideas from other folks.


---

*Resurrected by Resurrection Bot 🧬*
