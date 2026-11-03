from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int


def split_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(TextChunk(piece, index))
            index += 1
        if end >= len(normalized):
            break
        start = max(0, end - overlap)
    return chunks
