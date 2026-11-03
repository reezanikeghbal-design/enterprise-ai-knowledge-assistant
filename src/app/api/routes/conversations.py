from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/conversations", tags=["conversations"])


def configure(service):
    @router.get("")
    async def list_conversations():
        return service.list()

    @router.get("/{conversation_id}")
    async def get_conversation(conversation_id: str):
        result = service.get(conversation_id)
        if result is None:
            raise HTTPException(404, "Conversation not found")
        return result

    return router
