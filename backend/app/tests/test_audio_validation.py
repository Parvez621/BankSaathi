import io
import wave

import pytest

from app.services.audio_validation import (
    AudioValidationError,
    validate_audio,
)


def make_wav(duration=1, sample_rate=16000, channels=1):
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        samples = int(duration * sample_rate)
        wav.writeframes(
            b"\x00\x00" * samples * channels
        )

    return buffer.getvalue()


def test_valid_audio():
    audio = make_wav()
    metadata = validate_audio(audio)

    assert metadata.duration_seconds == 1.0
    assert metadata.sample_rate == 16000
    assert metadata.channels == 1


def test_empty_audio():
    with pytest.raises(AudioValidationError):
        validate_audio(b"")


def test_invalid_format():
    with pytest.raises(AudioValidationError):
        validate_audio(b"not a wave file")


def test_audio_too_long():
    audio = make_wav(duration=31)

    with pytest.raises(AudioValidationError):
        validate_audio(audio)


def test_invalid_sample_rate():
    audio = make_wav(sample_rate=44100)

    with pytest.raises(AudioValidationError):
        validate_audio(audio)


def test_stereo_audio_rejected():
    audio = make_wav(channels=2)

    with pytest.raises(AudioValidationError):
        validate_audio(audio)
