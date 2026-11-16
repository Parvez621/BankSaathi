
from dataclasses import dataclass
from typing import Protocol

from app.services.audio_validation import AudioMetadata


@dataclass(frozen=True)
class TranscriptionResult:
    transcript: str
    language: str
    simulated: bool


class SpeechProvider(Protocol):
    async def transcribe(
        self,
        audio: bytes,
        language: str,
        metadata: AudioMetadata,
    ) -> TranscriptionResult:
        ...


class MockSpeechProvider:
    """Development-only provider. Performs no real transcription."""

    async def transcribe(
        self,
        audio: bytes,
        language: str,
        metadata: AudioMetadata,
    ) -> TranscriptionResult:
        return TranscriptionResult(
            transcript="[MOCK] Transcription not performed",
            language=language,
            simulated=True,
        )
