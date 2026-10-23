# Richer Interface for Multimodal Data and BaseChat Interaction

**Repository:** [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
**Issue:** [langchain-ai/langchain#33056](https://github.com/langchain-ai/langchain/issues/33056)
**Reactions:** 5 👍
**Created:** 2025-09-23T17:05:46Z
**Last Activity:** 2026-06-11T07:28:24Z
**Labels:** feature request, external

---

## Original Description

### Checked other resources

- [x] This is a feature request, not a bug report or usage question.
- [x] I added a clear and descriptive title that summarizes the feature request.
- [x] I used the GitHub search to find a similar feature request and didn't find it.
- [x] I checked the LangChain documentation and API reference to see if this feature already exists.
- [x] This is not related to the langchain-community package.

### Feature Description

Based on my experience with Langchain, I find the `langchain.Document` interface to be too generic—perhaps intentionally so, to support a wide range of use cases. However, as LLMs continue to evolve, especially with growing multimodal capabilities, the need for a richer, more expressive interface for data parsing, storage, retrieval, LLM interaction, and citation becomes increasingly critical.
Currently, `Langchain.Document` is not expressive enough to represent complex or structured information beyond plain text. I also explored `Langchain.BaseMedia`, which partially addresses multimodality (e.g., image/audio), but it still lacks the granularity required for representing tables, formulas, and other structured formats. I’m expanding the concept of "modality" here to include more sophisticated constructs for representing information.

### Use Case

### Existing Gaps and Observations
There are interfaces in other systems that attempt to support richer representations, but many are tightly coupled with specific document parsers. For example:
* **[Docling](https://docling-project.github.io/docling/concepts/docling_document/#example-document-structures)** provides its own schema for structured outputs from parsed documents (text, tables, images, etc.).
* Other parser APIs like **LandingAI** or **LlamaParse** also return structured outputs (e.g., in JSON, HTML, Markdown).

This reveals a broader opportunity: to define a **common interface** in Langchain that can represent different modalities - `TextElement`, `ImageElement`, `TableElement`, `AudioElement`, etc. - as part of a unified `MultimodalDocument`, which could be implemented as something like `List[Element]`.
Such a structure could assume vertically stacked elements by default, but it could also support layout-aware metadata (e.g., page number, bounding boxes) if the parser is capable of providing it.
Currently, most Langchain chains/runnables (e.g., for Q\&A) are text-based. They expect retrievers to return a `List[Document]` where the content is textual. These documents are typically concatenated into a prompt string passed to the LLM.
However, in the multimodal setting, this approach doesn’t scale well. You need to interact with the LLM using `HumanMessage` objects that might represent different modalities. The current workaround - dumping everything into `Document.metadata` and reconstructing `HumanMessage` types (text, image, etc.) from there - is hacky, hard to reuse, and error-prone.

There’s a clear **design gap** here:
* Langchain expects ret

---

*Resurrected by Resurrection Bot 🧬*
