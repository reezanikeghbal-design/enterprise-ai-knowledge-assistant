from __future__ import annotations

import csv
import io
import logging
from pathlib import Path
from typing import BinaryIO

import fitz
from docx import Document

from app.core.exceptions import DuplicateDocumentError, InvalidDocumentError
from app.core.config import Settings
from app.services.embedding_service import EmbeddingService
from app.storage.vector_store import VectorStore
from app.utils.chunking import split_text
from app.utils.text_processing import safe_filename, sha256_bytes

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, settings: Settings, vector_store: VectorStore, embeddings: EmbeddingService):
        self.settings = settings
        self.vector_store = vector_store
        self.embeddings = embeddings
        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    def _extract(self, filename: str, data: bytes) -> list[dict]:
        ext = Path(filename).suffix.lower().lstrip(".")
        if ext == "pdf":
            try:
                doc = fitz.open(stream=data, filetype="pdf")
                return [{"text": page.get_text(), "page": i + 1} for i, page in enumerate(doc)]
            except Exception as exc:
                raise InvalidDocumentError(f"Could not read PDF: {exc}") from exc
        if ext == "docx":
            try:
                doc = Document(io.BytesIO(data))
                text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
                return [{"text": text, "page": None}]
            except Exception as exc:
                raise InvalidDocumentError(f"Could not read DOCX: {exc}") from exc
        if ext == "txt":
            try:
                return [{"text": data.decode("utf-8"), "page": None}]
            except UnicodeDecodeError as exc:
                raise InvalidDocumentError("TXT must be UTF-8 encoded") from exc
        if ext == "csv":
            try:
                rows = csv.reader(io.StringIO(data.decode("utf-8")))
                text = "\n".join(" | ".join(row) for row in rows)
                return [{"text": text, "page": None}]
            except Exception as exc:
                raise InvalidDocumentError(f"Could not read CSV: {exc}") from exc
        raise InvalidDocumentError("Unsupported file type")

    def ingest(self, filename: str, data: bytes) -> dict:
        filename = safe_filename(filename)
        ext = Path(filename).suffix.lower().lstrip(".")
        if ext not in self.settings.allowed_extensions_set:
            raise InvalidDocumentError(f"Unsupported extension: {ext}")
        max_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        if len(data) > max_bytes:
            raise InvalidDocumentError("File exceeds configured size limit")

        file_hash = sha256_bytes(data)
        if self.vector_store.document_exists(file_hash):
            raise DuplicateDocumentError("This document has already been ingested")

        pages = self._extract(filename, data)
        all_chunks = []
        for page in pages:
            for chunk in split_text(page["text"], self.settings.chunk_size, self.settings.chunk_overlap):
                all_chunks.append({
                    "text": chunk.text,
                    "page": page["page"],
                    "chunk_index": chunk.chunk_index,
                })
        if not all_chunks:
            raise InvalidDocumentError("Document contains no extractable text")

        document_id = file_hash[:16]
        destination = Path(self.settings.upload_dir) / f"{document_id}_{filename}"
        destination.write_bytes(data)

        texts = [c["text"] for c in all_chunks]
        vectors = self.embeddings.embed(texts)
        metadata = [
            {
                "document_id": document_id,
                "document_name": filename,
                "file_hash": file_hash,
                "page": c["page"] if c["page"] is not None else -1,
                "chunk_index": c["chunk_index"],
                "source": f"{filename}#chunk-{c['chunk_index']}",
            }
            for c in all_chunks
        ]
        ids = [f"{document_id}-{i}" for i in range(len(all_chunks))]
        self.vector_store.add(ids, texts, vectors, metadata)
        return {
            "document_id": document_id,
            "document_name": filename,
            "file_hash": file_hash,
            "chunks": len(all_chunks),
        }
