from app.core.config import Settings
from app.services.embedding_service import EmbeddingService
from app.storage.vector_store import VectorStore


class RetrievalService:
    def __init__(self, settings: Settings, store: VectorStore, embeddings: EmbeddingService):
        self.settings = settings
        self.store = store
        self.embeddings = embeddings

    def search(self, query: str, top_k: int | None = None, threshold: float | None = None) -> list[dict]:
        top_k = top_k or self.settings.top_k
        threshold = self.settings.similarity_threshold if threshold is None else threshold
        result = self.store.search(self.embeddings.embed_one(query), top_k)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        output = []
        for text, md, distance in zip(docs, metas, distances):
            score = max(0.0, 1.0 - float(distance))
            if score >= threshold:
                output.append({
                    "text": text,
                    "document_name": md["document_name"],
                    "document_id": md["document_id"],
                    "page": None if md.get("page", -1) == -1 else md.get("page"),
                    "source": md["source"],
                    "score": round(score, 4),
                })
        return output
