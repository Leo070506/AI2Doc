"""Conversion endpoint supporting JSON and Markdown uploads."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from app.errors import (
    FileTooLargeError,
    InvalidEncodingError,
    InvalidRequestError,
    InvalidTemplateError,
    UnsupportedMediaTypeError,
)
from app.models.api import ConvertResponse, ConvertTextRequest

router = APIRouter(prefix="/api", tags=["conversion"])


def _reject_oversized_request(request: Request, overhead_bytes: int) -> None:
    content_length = request.headers.get("content-length")
    if content_length is None:
        return
    try:
        request_bytes = int(content_length)
    except ValueError as exc:
        raise InvalidRequestError() from exc
    if request_bytes > request.app.state.settings.max_input_bytes + overhead_bytes:
        raise FileTooLargeError()


async def _read_json(request: Request) -> tuple[str, str]:
    settings = request.app.state.settings
    raw = await request.body()
    if len(raw) > settings.max_input_bytes + 64 * 1024:
        raise FileTooLargeError()
    try:
        payload = ConvertTextRequest.model_validate_json(raw)
    except ValidationError as exc:
        errors = exc.errors()
        if any(error.get("loc") == ("template",) for error in errors):
            raise InvalidTemplateError() from exc
        raise InvalidRequestError() from exc
    return payload.content, payload.template


async def _read_multipart(request: Request) -> tuple[str, str]:
    settings = request.app.state.settings
    form = await request.form()
    upload = form.get("file")
    template = form.get("template")
    if not isinstance(upload, UploadFile) or not isinstance(template, str):
        raise InvalidRequestError()
    if not upload.filename or not upload.filename.casefold().endswith((".md", ".markdown")):
        raise UnsupportedMediaTypeError()
    if template not in {"academic", "report", "notes"}:
        raise InvalidTemplateError()

    data = await upload.read(settings.max_input_bytes + 1)
    await upload.close()
    if len(data) > settings.max_input_bytes:
        raise FileTooLargeError()
    try:
        return data.decode("utf-8-sig"), template
    except UnicodeDecodeError as exc:
        raise InvalidEncodingError() from exc


@router.post(
    "/convert",
    response_model=ConvertResponse,
    summary="Convert Markdown to DOCX",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["content", "template"],
                        "properties": {
                            "content": {"type": "string"},
                            "template": {
                                "type": "string",
                                "enum": ["academic", "report", "notes"],
                            },
                        },
                    }
                },
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["file", "template"],
                        "properties": {
                            "file": {"type": "string", "format": "binary"},
                            "template": {
                                "type": "string",
                                "enum": ["academic", "report", "notes"],
                            },
                        },
                    }
                },
            }
        }
    },
)
async def convert(request: Request) -> ConvertResponse:
    content_type = request.headers.get("content-type", "").casefold()
    if content_type.startswith("application/json"):
        _reject_oversized_request(request, 64 * 1024)
        content, template = await _read_json(request)
    elif content_type.startswith("multipart/form-data"):
        _reject_oversized_request(request, 256 * 1024)
        content, template = await _read_multipart(request)
    else:
        raise UnsupportedMediaTypeError()

    artifact = await run_in_threadpool(
        request.app.state.conversion_service.convert,
        content,
        template,
    )
    return ConvertResponse(
        file=f"/api/files/{artifact.token}",
        filename=artifact.filename,
        expires_at=artifact.expires_at.isoformat(),
    )
