from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.exceptions import DuplicateDocumentError, InvalidDocumentError

router = APIRouter(prefix="/documents", tags=["documents"])


def configure(service):
    @router.post("/upload")
    async def upload(file: UploadFile = File(...)):
        try:
            data = await file.read()
            return service.ingest(file.filename or "document", data)
        except DuplicateDocumentError as exc:
            raise HTTPException(409, str(exc))
        except InvalidDocumentError as exc:
            raise HTTPException(400, str(exc))

    @router.get("")
    async def list_documents():
        return service.vector_store.list_documents()

    @router.delete("/{document_id}")
    async def delete_document(document_id: str):
        service.vector_store.delete_document(document_id)
        return {"deleted": document_id}

    return router
