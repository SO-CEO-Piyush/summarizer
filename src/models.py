import logging
import os
import typing
from urllib.parse import urlparse

from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)

SUPPORTED_DOC_EXTENSIONS = [
    ".pdf",
    ".pptx",
    ".ppt",
    ".docx",
    ".doc",
    ".txt",
    ".xlsx",
    ".xls",
]


class SummaryRequest(BaseModel):
    url: typing.Optional[str] = None
    text: typing.Optional[str] = None
    custom_instructions: typing.Optional[str] = None

    @model_validator(mode="after")
    def check_url_or_text(self):
        logger.warning("check_url_or_text")
        if self.url and self.text:
            raise ValueError("provide either url or text, not both")
        if not self.url and not self.text:
            raise ValueError("provide either url or text")
        if self.url and not self.url.endswith("/"):
            self.url = self.url + "/"
        if self.url:
            logger.warning("HERRRRRR")
            parsed = urlparse(self.url)
            path = parsed.path.lower().rstrip("/")
            if path:
                path_ext = os.path.splitext(path)[1]
                print(f"HELLOOOO {path_ext}")
                if (
                    path_ext
                    and path_ext not in SUPPORTED_DOC_EXTENSIONS
                    and path_ext not in ["", ".html", ".htm"]
                ):
                    raise ValueError(
                        f"unsupported document type: {path_ext}. supported types: {', '.join(SUPPORTED_DOC_EXTENSIONS)}"
                    )
        return self


class SummaryResultResponse(SummaryRequest):
    job_id: int
    is_cached: bool
    result: str
