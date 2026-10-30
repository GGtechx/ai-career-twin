"""
Text extraction utilities for PDF resume parsing.
Handles PDF reading with pdfplumber (primary) and pypdf (fallback).
"""
import re
import io
import logging
from typing import Optional

logger = logging.getLogger("app.utils.text_extraction")

def extract_text_from_pdf_bytes(file_bytes: bytes) -> tuple[str, str]:
    """
    Extracts text from PDF bytes.
    Returns (extracted_text, method_used).
    Tries pdfplumber first (best layout preservation), then pypdf as fallback.
    Raises ValueError if no text can be extracted.
    """
    raw_text = ""

    # --- Primary: pdfplumber ---
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            raw_text = "\n".join(pages_text)
        if raw_text.strip():
            logger.info("PDF text extracted using pdfplumber")
            return raw_text, "pdfplumber"
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")

    # --- Fallback: pypdf ---
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        raw_text = "\n".join(pages_text)
        if raw_text.strip():
            logger.info("PDF text extracted using pypdf fallback")
            return raw_text, "pypdf"
    except Exception as e:
        logger.warning(f"pypdf extraction also failed: {e}")

    if not raw_text.strip():
        raise ValueError("Could not extract any readable text from the PDF. The file may be image-based or corrupted.")

    return raw_text, "unknown"


def clean_text(raw_text: str) -> str:
    """
    Cleans extracted PDF text:
    - Removes excessive whitespace and blank lines
    - Normalizes unicode characters
    - Collapses repeated punctuation
    """
    if not raw_text:
        return ""

    text = raw_text.strip()
    # Normalize unicode dashes, bullets and similar
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2022", " ")
    text = text.replace("\u00e2\u20ac\u00b2", "'").replace("\u00e2\u20ac\u201c", "-")
    # Remove page headers/footers (lines that are purely numbers or very short)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Keep non-trivial lines
        if len(stripped) > 1:
            cleaned_lines.append(stripped)
    text = "\n".join(cleaned_lines)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
