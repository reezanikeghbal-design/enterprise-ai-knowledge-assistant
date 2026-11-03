import hashlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_filename(name: str) -> str:
    name = Path(name).name
    cleaned = "".join(c for c in name if c.isalnum() or c in "._- ")
    return cleaned.strip() or "document"
