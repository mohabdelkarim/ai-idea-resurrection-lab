# RFC: Richer Interface for Multimodal Data and BaseChat Interaction

1. Summary
The proposal introduces a RichDocument class to replace the current Document model in LangChain. RichDocument is a Pydantic v2‑based, hierarchical container that can hold heterogeneous content parts such as images, tables, formulas, and plain text. The design adds a ContentPart interface, concrete MediaComponent, TableComponent, and FormulaComponent implementations, and a ContentPartFactory that selects the appropriate component based on MIME type or file extension. Existing parsers are wrapped with adapters that emit RichDocument parts, preserving backward compatibility. Retrieval pipelines and prompt builders are extended to accept RichDocument and automatically serialize its parts for multimodal LLMs (e.g., GPT‑4V, Claude‑3 Vision). The change leverages the new "langchain-schema" package and Pydantic v2, providing type‑safe validation, OpenAPI schema generation, and easy extensibility.

2. Motivation
Since 2025 multimodal LLMs have become production‑ready, and users increasingly need to feed structured artifacts (tables, diagrams, LaTeX formulas) alongside text. The current Document model stores a single "page_content" string and an optional metadata dict, which forces callers to flatten complex objects into text or lose information entirely. This leads to sub‑optimal prompting, higher preprocessing cost, and duplicated parsing logic across projects. With the recent introduction of a pluggable schema system and native Pydantic v2 support, LangChain now has the technical foundation to expose a richer, type‑checked document abstraction without breaking existing code. Providing a unified multimodal interface will reduce boilerplate, improve prompt fidelity, and position LangChain as the go‑to framework for next‑generation LLM applications.

3. Detailed Design
- **Base Classes**: Introduce `BaseDocument` (unchanged) and `RichDocument(BaseDocument)`. RichDocument contains a list of `ContentPart` objects and optional hierarchical children.
- **ContentPart Interface**: Defines `mime_type: str`, `serialize() -> dict`, and `to_prompt() -> str | bytes` methods.
- **Concrete Parts**:
  * `MediaComponent` for images, audio, video (stores binary data as `bytes` or a file path).
  * `TableComponent` for CSV/Excel/HTML tables (stores a Pandas DataFrame and optional schema).
  * `FormulaComponent` for LaTeX or MathML (stores raw string and rendered PNG fallback).
- **Factory**: `ContentPartFactory.from_file(path: str) -> ContentPart` inspects file extension/MIME and returns the correct component.
- **Adapters**: Wrapper classes for existing parsers (e.g., `PDFParserAdapter`) that emit `RichDocument` instead of plain `Document`.
- **Pipeline Integration**: Extend `BaseRetriever` and `BasePromptBuilder` signatures to accept `RichDocument`. The prompt builder iterates over parts, calling `to_prompt()` and concatenating results with appropriate LLM‑specific tags (e.g., `<image>`, `<table>`).
- **Serialization**: Leverage Pydantic v2's `model_dump_json()` to produce OpenAPI‑compatible schemas. RichDocument can be stored in vector stores as a JSON blob while preserving part metadata.
- **Backward Compatibility**: Existing code that expects `Document` will continue to work because `RichDocument` inherits from it and provides a `page_content` property that concatenates textual parts.
- **Testing & Documentation**: Add unit tests for factory mapping, serialization round‑trip, and end‑to‑end retrieval with a multimodal LLM mock. Generate API docs via `mkdocstrings` and expose OpenAPI spec through the new `langchain-schema` utilities.

4. Drawbacks
- **Increased Complexity**: Introducing multiple component classes adds a learning curve for new contributors and may increase the maintenance burden.
- **Performance Overhead**: Serializing large binary blobs (e.g., high‑resolution images) into JSON can inflate memory usage and network transfer size. Careful chunking or external storage references will be required.
- **Breaking Change Risk**: Although we inherit from `BaseDocument`, some downstream libraries may rely on the exact shape of `metadata` and could encounter subtle incompatibilities.
- **Dependency on Pydantic v2**: Projects still on Pydantic v1 will need to upgrade or use a compatibility shim, which could delay adoption.

5. Alternatives
- **Flat Extension**: Add optional fields (`image_path`, `table_data`) directly to the existing `Document` model. This is simpler but scales poorly as more modalities appear.
- **External Wrapper**: Keep `Document` unchanged and create a separate `MultimodalDocument` that holds a reference to a `Document`. This avoids inheritance issues but forces callers to manage two objects.
- **Plugin‑Only Approach**: Provide a community‑maintained plugin that implements multimodal parts without altering core classes. This reduces core impact but fragments the ecosystem and requires extra boilerplate for each project.

6. Unresolved Questions
- How should large binary assets be stored? Should we embed them as base64, reference a CDN, or rely on vector‑store side‑car files?
- What is the optimal default serialization format for tables (CSV vs. JSON vs. Parquet) to balance readability and size?
- Should the factory support streaming sources (e.g., live video frames) or only static files?
- How will versioning of the RichDocument schema be communicated to downstream vector‑store providers?
- What fallback behavior is desired when a downstream LLM does not support a particular modality?
- Is there a need for a user‑configurable “part priority” to control ordering in prompts?

---

*RFC generated by Resurrection Bot 🧬*
