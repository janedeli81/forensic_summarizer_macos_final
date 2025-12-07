# text_extraction.py

from pathlib import Path
from typing import Optional

import docx
import pdfplumber


def extract_text(path: Path) -> Optional[str]:
    """
    Read text content from .docx, .pdf, or .txt file.
    Returns None if file format is unsupported.
    """
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return _extract_docx(path)
    elif suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    else:
        return None


def _extract_docx(path: Path) -> str:
    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_pdf(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)
