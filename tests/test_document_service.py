from app.core.config import Settings
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
