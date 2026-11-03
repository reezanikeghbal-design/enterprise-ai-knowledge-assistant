from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.exceptions import DuplicateDocumentError, InvalidDocumentError

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_READ_CHUNK_SIZE = 1024 * 1024


async def _read_upload_with_limit(file: UploadFile, max_bytes: int) -> bytes:
    """Read an upload incrementally and stop as soon as it exceeds max_bytes."""
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    if file.size is not None and file.size > max_bytes:
        raise InvalidDocumentError("File exceeds configured size limit")

    chunks: list[bytes] = []
    total_bytes = 0

    while True:
        chunk = await file.read(UPLOAD_READ_CHUNK_SIZE)
        if not chunk:
            break

        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise InvalidDocumentError("File exceeds configured size limit")

        chunks.append(chunk)

    return b"".join(chunks)


def configure(service):
    @router.post("/upload")
    async def upload(file: UploadFile = File(...)):
        max_bytes = service.settings.max_upload_size_mb * 1024 * 1024
        try:
            data = await _read_upload_with_limit(file, max_bytes)
            return service.ingest(file.filename or "document", data)
        except DuplicateDocumentError as exc:
            raise HTTPException(409, str(exc))
        except InvalidDocumentError as exc:
            raise HTTPException(400, str(exc))
        finally:
            await file.close()

    @router.get("")
    async def list_documents():
        return service.vector_store.list_documents()

    @router.delete("/{document_id}")
    async def delete_document(document_id: str):
        service.vector_store.delete_document(document_id)
        return {"deleted": document_id}

    return router
