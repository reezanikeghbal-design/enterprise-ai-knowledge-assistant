from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
