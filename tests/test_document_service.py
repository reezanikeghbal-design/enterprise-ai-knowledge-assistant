import asyncio
import io

import pytest
from starlette.datastructures import UploadFile

from app.core.config import Settings
from app.core.exceptions import InvalidDocumentError
from app.api.routes.documents import _read_upload_with_limit
from app.services.document_service import DocumentService
from app.utils.text_processing import sha256_bytes


class FakeEmbeddings:
    def embed(self, texts):
        return [[0.1, 0.2] for _ in texts]


class FakeStore:
    def __init__(self):
        self.added = []

    def document_exists(self, file_hash):
        return False

    def add(self, ids, texts, embeddings, metadata):
        self.added.append((ids, texts, embeddings, metadata))


def test_txt_ingestion(tmp_path):
    settings = Settings(
        upload_dir=str(tmp_path / "uploads"),
        max_upload_size_mb=1,
        chunk_size=50,
        chunk_overlap=5,
    )
    store = FakeStore()
    service = DocumentService(settings, store, FakeEmbeddings())
    data = b"hello enterprise knowledge assistant"
    result = service.ingest("test.txt", data)
    assert result["file_hash"] == sha256_bytes(data)
    assert result["chunks"] >= 1
    assert store.added


def test_ingestion_rejects_oversized_data(tmp_path):
    settings = Settings(
        upload_dir=str(tmp_path / "uploads"),
        max_upload_size_mb=1,
    )
    service = DocumentService(settings, FakeStore(), FakeEmbeddings())

    with pytest.raises(InvalidDocumentError, match="size limit"):
        service.ingest("large.txt", b"x" * (1024 * 1024 + 1))


def test_upload_reader_accepts_file_within_limit():
    upload = UploadFile(filename="small.txt", file=io.BytesIO(b"small file"))
    result = asyncio.run(_read_upload_with_limit(upload, max_bytes=20))
    assert result == b"small file"


def test_upload_reader_rejects_file_over_limit():
    upload = UploadFile(filename="large.txt", file=io.BytesIO(b"x" * 11))
    with pytest.raises(InvalidDocumentError, match="size limit"):
        asyncio.run(_read_upload_with_limit(upload, max_bytes=10))


def test_upload_reader_rejects_using_declared_size():
    upload = UploadFile(filename="large.txt", file=io.BytesIO(b"x"), size=11)
    with pytest.raises(InvalidDocumentError, match="size limit"):
        asyncio.run(_read_upload_with_limit(upload, max_bytes=10))
