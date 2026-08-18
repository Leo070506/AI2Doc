"""Public API request and response schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

TemplateName = Literal["academic", "report", "notes"]


class ConvertTextRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str
    template: TemplateName


class ConvertResponse(BaseModel):
    status: Literal["success"] = "success"
    file: str
    filename: str
    expires_at: str
