from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    conversation_id: str | None = None


class Source(BaseModel):
    document_name: str
    document_id: str
    text: str
    page: int | None = None
    source: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: list[Source]
