from pathlib import Path

from pydantic_ai import BinaryContent


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


def read_contract_text(path: Path) -> str:
    """Read the contract text.

    Supports:
    - .txt / .md: read directly as UTF-8 text
    - .pdf: extract text via pypdf

    Diese Implementierung ist bewusst einfach gehalten (reiner Textlayer,
    keine OCR). Falls dein Vertrag ein gescanntes PDF ohne Textlayer ist,
    müsste hier zusätzlich OCR (z.B. via pytesseract) ergänzt werden.
    """
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages_text).strip()
        if not text:
            raise ValueError(
                f"Konnte keinen Text aus '{path}' extrahieren. "
                "Falls es sich um ein gescanntes PDF ohne Textlayer handelt, "
                "wird OCR benötigt (hier nicht implementiert)."
            )
        return text

    raise ValueError(
        f"Nicht unterstütztes Vertragsformat: '{suffix}' (erwartet .txt, .md oder .pdf)"
    )
