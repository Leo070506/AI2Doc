"""One-time generated document download endpoint."""

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api", tags=["downloads"])


@router.get("/files/{token}", summary="Download a generated DOCX once")
async def download(token: str, request: Request, background_tasks: BackgroundTasks) -> FileResponse:
    artifact = request.app.state.file_store.claim(token)
    background_tasks.add_task(request.app.state.file_store.delete_workspace, artifact.path.parent)
    return FileResponse(
        artifact.path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=artifact.filename,
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
        background=background_tasks,
    )
