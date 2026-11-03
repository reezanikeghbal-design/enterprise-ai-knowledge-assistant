from fastapi import APIRouter
from app.api.schemas.search import SearchRequest

router = APIRouter(tags=["search"])


def configure(retrieval):
    @router.post("/search")
    async def search(request: SearchRequest):
        return retrieval.search(request.query, request.top_k, request.similarity_threshold)
    return router
