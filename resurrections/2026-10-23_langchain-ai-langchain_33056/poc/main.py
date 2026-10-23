import json
import os
import mimetypes
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# BaseDocument mimics LangChain's Document
@dataclass
class BaseDocument:
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

# ContentPart interface
class ContentPart(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

# MediaComponent for images/audio etc.
@dataclass
class MediaComponent(ContentPart):
    mime_type: str
    data: bytes
    caption: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "media",
            "mime_type": self.mime_type,
            "size": len(self.data),
            "caption": self.caption,
        }

# TableComponent for simple tables
@dataclass
class TableComponent(ContentPart):
    headers: List[str]
    rows: List[List[Any]]
    title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "table",
            "title": self.title,
            "headers": self.headers,
            "rows": self.rows,
        }

# FormulaComponent for LaTeX or similar
@dataclass
class FormulaComponent(ContentPart):
    formula: str
    language: str = "latex"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "formula",
            "language": self.language,
            "formula": self.formula,
        }

# Factory to create appropriate ContentPart based on mime or extension
class ContentPartFactory:
    @staticmethod
    def create_from_file(path: str) -> ContentPart:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        mime, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            data = f.read()
        if mime and mime.startswith("image"):
            return MediaComponent(mime_type=mime, data=data)
        elif mime == "text/plain":
            # naive detection: if contains tabular structure assume table
            text = data.decode(errors="ignore")
            if "\t" in text:
                lines = text.strip().split("\n")
                headers = lines[0].split("\t")
                rows = [line.split("\t") for line in lines[1:]]
                return TableComponent(headers=headers, rows=rows)
            else:
                return MediaComponent(mime_type=mime, data=data)
        else:
            # fallback to generic media
            return MediaComponent(mime_type=mime or "application/octet-stream", data=data)

# RichDocument extending BaseDocument with hierarchical parts
@dataclass
class RichDocument(BaseDocument):
    parts: List[ContentPart] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)

    def add_part(self, part: ContentPart) -> None:
        self.parts.append(part)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_content": self.page_content,
            "metadata": self.metadata,
            "parts": [p.to_dict() for p in self.parts],
            "citations": self.citations,
        }

# Simple adapter that pretends to parse raw text into RichDocument parts
class SimpleParserAdapter:
    def __init__(self, source: str):
        self.source = source

    def parse(self) -> RichDocument:
        doc = RichDocument(page_content=self.source, metadata={"source": "simple_adapter"})
        # naive split by markers
        for line in self.source.split("\n"):
            line = line.strip()
            if line.startswith("[IMG]"):
                path = line[5:].strip()
                try:
                    part = ContentPartFactory.create_from_file(path)
                    doc.add_part(part)
                except Exception as e:
                    doc.metadata.setdefault("errors", []).append(str(e))
            elif line.startswith("[TABLE]"):
                # expect next lines to be CSV-like until empty line
                continue  # placeholder for brevity
        return doc

# Mock retrieval pipeline that accepts RichDocument
def retrieval_pipeline(doc: RichDocument) -> str:
    # Build a prompt string using parts
    prompt = f"Document: {doc.page_content}\n"
    for idx, part in enumerate(doc.parts):
        prompt += f"Part {idx+1}: {json.dumps(part.to_dict())}\n"
    # In real scenario, send to LLM; here just return prompt
    return prompt

# Unit-test style demonstration
if __name__ == "__main__":
    # Create a temporary image file for demo
    img_path = "demo_image.png"
    try:
        with open(img_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # minimal PNG header
        raw_text = f"This is a sample document.\n[IMG] {img_path}\nEnd of doc."
        adapter = SimpleParserAdapter(raw_text)
        rich_doc = adapter.parse()
        output = retrieval_pipeline(rich_doc)
        print(output)
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)