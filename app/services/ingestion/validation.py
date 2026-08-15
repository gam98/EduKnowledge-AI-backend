import hashlib
from urllib.parse import urlparse

from fastapi import HTTPException

ALLOWED_TYPES = {"text/plain": "manual", "text/csv": "csv", "application/pdf": "pdf"}


def validate_upload(content: bytes, content_type: str, max_bytes: int = 10_000_000) -> str:
    if not content or len(content) > max_bytes:
        raise HTTPException(422, "Invalid document size")
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Unsupported document type")
    return ALLOWED_TYPES[content_type]


def validate_url(url: str, allowed_domains: set[str]) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.hostname not in allowed_domains:
        raise HTTPException(422, "URL domain is not allowed")
    return url


def checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def extract_text(content: bytes, source_type: str) -> str:
    if source_type == "pdf":
        if not content.startswith(b"%PDF"):
            raise HTTPException(422, "Invalid PDF file")
        raise HTTPException(501, "PDF extraction adapter is not configured")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "Document must be UTF-8") from exc


def chunk_text(text: str, size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + size]))
        start += max(1, size - overlap)
    return chunks
