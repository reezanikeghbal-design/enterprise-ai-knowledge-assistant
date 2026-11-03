from pathlib import Path

from fastapi import Depends, FastAPI

from app.api.routes import documents, chat, search, conversations, evaluation
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.security import require_api_key
from app.evaluation.evaluator import Evaluator
from app.services.conversation_service import ConversationService
from app.services.document_service import DocumentService
from app.services.embedding_service import get_embedding_service
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.storage.vector_store import VectorStore

configure_logging()
settings = get_settings()
Path(settings.data_dir).mkdir(parents=True, exist_ok=True)

vector_store = VectorStore(settings.chroma_dir)
embeddings = get_embedding_service(settings.embedding_model)
document_service = DocumentService(settings, vector_store, embeddings)
retrieval_service = RetrievalService(settings, vector_store, embeddings)
rag_service = RAGService(settings, retrieval_service)
conversation_service = ConversationService(settings.conversation_file)
evaluator = Evaluator(
    retrieval_service,
    rag_service,
    str(Path("evaluation") / "dataset.json"),
)

app = FastAPI(title=settings.app_name, version="1.0.0")
protected = [Depends(require_api_key)]

app.include_router(documents.configure(document_service), dependencies=protected)
app.include_router(chat.configure(rag_service, conversation_service), dependencies=protected)
app.include_router(search.configure(retrieval_service), dependencies=protected)
app.include_router(conversations.configure(conversation_service), dependencies=protected)
app.include_router(evaluation.configure(evaluator), dependencies=protected)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "service": settings.app_name}
