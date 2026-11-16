
import secrets

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from starlette.datastructures import UploadFile
from starlette.requests import Request as StarletteRequest

from app.core.config import get_settings
from app.services.audio_validation import (
    MAX_AUDIO_SIZE,
    AudioValidationError,
    validate_audio,
)
from app.services.transcription import MockSpeechProvider


router = APIRouter(prefix="/speech", tags=["Speech"])

MAX_REQUEST_SIZE = MAX_AUDIO_SIZE + 64 * 1024


class TranscriptionResponse(BaseModel):
    transcript: str
    language: str
    requires_confirmation: bool
    simulated: bool


async def read_bounded_body(request: Request) -> bytes:
    """Enforce an upload limit before multipart parsing."""

    content_length = request.headers.get("content-length")

    if content_length is not None:
        try:
            size = int(content_length)
        except ValueError:
            raise HTTPException(400, "Invalid Content-Length")

        if size < 0:
            raise HTTPException(400, "Invalid Content-Length")

        if size > MAX_REQUEST_SIZE:
            raise HTTPException(413, "Request too large")

    chunks = []
    total = 0

    async for chunk in request.stream():
        total += len(chunk)

        if total > MAX_REQUEST_SIZE:
            raise HTTPException(413, "Request too large")

        chunks.append(chunk)

    return b"".join(chunks)


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
)
async def transcribe_audio(
    request: Request,
    x_api_key: str | None = Header(default=None),
):
    settings = get_settings()

    if not settings.speech_api_key:
        raise HTTPException(
            503, "Speech API is not configured"
        )

    if not x_api_key or not secrets.compare_digest(
        x_api_key, settings.speech_api_key
    ):
        raise HTTPException(401, "Unauthorized")

    if settings.app_env != "development":
        raise HTTPException(
            503, "Real speech provider is not configured"
        )

    content_type = request.headers.get("content-type", "")

    if content_type.split(";")[0].strip().lower() != (
        "multipart/form-data"
    ):
        raise HTTPException(
            415, "Expected multipart/form-data"
        )

    body = await read_bounded_body(request)

    # Reconstruct an isolated, size-bounded request.
    delivered = False

    async def receive():
        nonlocal delivered

        if not delivered:
            delivered = True
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    bounded_request = StarletteRequest(
        request.scope,
        receive=receive,
    )

    async with bounded_request.form(
        max_files=1,
        max_fields=2,
        max_part_size=128,
    ) as form:

        if len(form.multi_items()) != 2 or set(form.keys()) != {
            "file", "language"
        }:
            raise HTTPException(
                422, "Expected one file and one language"
            )

        uploaded = form.get("file")
        language = form.get("language")

        if not isinstance(uploaded, UploadFile):
            raise HTTPException(
                422, "Valid audio file required"
            )

        if not isinstance(language, str) or language not in (
            "hi", "en"
        ):
            raise HTTPException(
                422, "Language must be hi or en"
            )

        if uploaded.size is not None and (
            uploaded.size > MAX_AUDIO_SIZE
        ):
            raise HTTPException(413, "Audio too large")

        audio = await uploaded.read(MAX_AUDIO_SIZE + 1)

        try:
            metadata = validate_audio(audio)
        except AudioValidationError as exc:
            raise HTTPException(
                422, str(exc)
            ) from exc

    provider = MockSpeechProvider()

    result = await provider.transcribe(
        audio=audio,
        language=language,
        metadata=metadata,
    )

    return TranscriptionResponse(
        transcript=result.transcript,
        language=result.language,
        requires_confirmation=True,
        simulated=result.simulated,
    )
