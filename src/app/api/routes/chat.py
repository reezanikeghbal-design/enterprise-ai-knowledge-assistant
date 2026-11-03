from fastapi import APIRouter, HTTPException

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.core.exceptions import LLMError

router = APIRouter(tags=["chat"])


def configure(rag, conversations):
    @router.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        conversation = conversations.get(request.conversation_id) if request.conversation_id else None
        if conversation is None:
            conversation = conversations.create()
        try:
            result = rag.chat(request.question, conversation["messages"])
        except LLMError as exc:
            raise HTTPException(503, str(exc))

        conversations.add_message(conversation["id"], "user", request.question)
        conversations.add_message(conversation["id"], "assistant", result["answer"])
        return {
            "answer": result["answer"],
            "conversation_id": conversation["id"],
            "sources": result["sources"],
        }

    return router
