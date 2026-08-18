"""Stable, user-safe API errors."""


class AI2DocError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class InvalidRequestError(AI2DocError):
    def __init__(self, message: str = "Invalid request") -> None:
        super().__init__(400, "invalid_request", message)


class FileTooLargeError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(413, "file_too_large", "File too large")


class UnsupportedMediaTypeError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(415, "unsupported_media_type", "Unsupported media type")


class EmptyContentError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(422, "empty_content", "Markdown content is empty")


class InvalidTemplateError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(422, "invalid_template", "Invalid template")


class InvalidEncodingError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(422, "invalid_encoding", "Markdown file must use UTF-8 encoding")


class DownloadNotFoundError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(404, "file_not_found", "File not found or already downloaded")


class PandocUnavailableError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(503, "pandoc_unavailable", "Pandoc unavailable")


class ConversionFailedError(AI2DocError):
    def __init__(self) -> None:
        super().__init__(500, "conversion_failed", "Conversion failed")
