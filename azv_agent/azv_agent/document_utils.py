from pathlib import Path

from pypdf import PdfReader
from pydantic_ai import BinaryContent


def read_contract_text(path: Path) -> str:
    """Extract text from the contract PDF for Agent 2."""
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise ValueError(f"No readable text found in contract: {path}")
    return text


def invoice_content(path: Path) -> BinaryContent:
    """Load an invoice image/PDF as multimodal content for Agent 1."""
    suffix = path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
    }
    if suffix not in media_types:
        raise ValueError("Invoice must be PNG, JPG, JPEG, WEBP, or PDF")
    return BinaryContent(data=path.read_bytes(), media_type=media_types[suffix])
