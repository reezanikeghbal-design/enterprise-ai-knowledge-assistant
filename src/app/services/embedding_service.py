from functools import lru_cache
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


@lru_cache(maxsize=4)
def get_embedding_service(model_name: str) -> EmbeddingService:
    return EmbeddingService(model_name)
