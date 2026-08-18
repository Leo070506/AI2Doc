"""Container and dependency health endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.templates.catalog import TEMPLATE_NAMES

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request):
    settings = request.app.state.settings
    templates = sorted(
        name
        for name in TEMPLATE_NAMES
        if (settings.templates_root / name / "template.docx").is_file()
    )
    try:
        request.app.state.file_store.ensure_storage()
        storage_available = settings.storage_root.is_dir()
    except OSError:
        storage_available = False

    if (
        request.app.state.pandoc_runner.is_available()
        and len(templates) == len(TEMPLATE_NAMES)
        and storage_available
    ):
        return {"status": "ready", "pandoc": "available", "templates": templates}
    return JSONResponse(status_code=503, content={"status": "unavailable"})
