import io
import wave

from dataclasses import dataclass


MAX_AUDIO_SIZE = 5 * 1024 * 1024
MAX_AUDIO_DURATION = 30
EXPECTED_SAMPLE_RATE = 16000


class AudioValidationError(Exception):
    """Raised when submitted audio fails validation."""


@dataclass(frozen=True)
class AudioMetadata:
    duration_seconds: float
    sample_rate: int
    channels: int
    sample_width: int
    size_bytes: int


def validate_audio(audio: bytes) -> AudioMetadata:
    """
    Validate uncompressed, mono, 16-bit PCM WAV audio.

    This function does not write audio to permanent storage.
    """

    if not audio:
        raise AudioValidationError("Audio file is empty.")

    if len(audio) > MAX_AUDIO_SIZE:
        raise AudioValidationError(
            "Audio exceeds the 5 MB limit."
        )

    # Check actual file signature, not its filename.
    if (
        len(audio) < 12
        or audio[:4] != b"RIFF"
        or audio[8:12] != b"WAVE"
    ):
        raise AudioValidationError(
            "Invalid audio format. Expected WAV."
        )

    try:
        with wave.open(io.BytesIO(audio), "rb") as wav:
            channels = wav.getnchannels()
            sample_rate = wav.getframerate()
            sample_width = wav.getsampwidth()
            frames = wav.getnframes()
            compression = wav.getcomptype()

            if compression != "NONE":
                raise AudioValidationError(
                    "Compressed WAV is not supported."
                )

            if channels != 1:
                raise AudioValidationError(
                    "Audio must be mono."
                )

            if sample_rate != EXPECTED_SAMPLE_RATE:
                raise AudioValidationError(
                    "Audio must use a 16000 Hz sample rate."
                )

            if sample_width != 2:
                raise AudioValidationError(
                    "Audio must use 16-bit samples."
                )

            if frames <= 0:
                raise AudioValidationError(
                    "Audio contains no samples."
                )

            duration = frames / sample_rate

            if duration > MAX_AUDIO_DURATION:
                raise AudioValidationError(
                    "Audio exceeds the 30-second limit."
                )

            # Verify the sample data is not truncated.
            expected_bytes = frames * channels * sample_width

            if expected_bytes > MAX_AUDIO_SIZE:
                raise AudioValidationError(
                    "Audio sample data is too large."
                )

            if len(wav.readframes(frames)) != expected_bytes:
                raise AudioValidationError(
                    "Audio sample data is incomplete."
                )

            return AudioMetadata(
                duration_seconds=round(duration, 3),
                sample_rate=sample_rate,
                channels=channels,
                sample_width=sample_width,
                size_bytes=len(audio),
            )

    except (wave.Error, EOFError, ValueError) as exc:
        raise AudioValidationError(
            "Invalid or unsupported WAV file."
        ) from exc
