from __future__ import annotations

from pathlib import Path
import chromadb


class VectorStore:
    def __init__(self, path: str):
        Path(path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, ids, texts, embeddings, metadata):
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadata)

    def search(self, embedding: list[float], top_k: int):
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

    def document_exists(self, file_hash: str) -> bool:
        result = self.collection.get(where={"file_hash": file_hash}, limit=1)
        return bool(result.get("ids"))

    def list_documents(self) -> list[dict]:
        data = self.collection.get(include=["metadatas"])
        grouped = {}
        for md in data.get("metadatas", []):
            if not md:
                continue
            did = md["document_id"]
            grouped.setdefault(did, {
                "document_id": did,
                "document_name": md["document_name"],
                "file_hash": md["file_hash"],
                "chunks": 0,
            })
            grouped[did]["chunks"] += 1
        return list(grouped.values())

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})
