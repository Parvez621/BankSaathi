
import io
import wave
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import speech


client = TestClient(app)
TEST_KEY = "testing-secret"


@pytest.fixture(autouse=True)
def configure_mock(monkeypatch):
    monkeypatch.setattr(
        speech,
        "get_settings",
        lambda: SimpleNamespace(
            speech_api_key=TEST_KEY,
            app_env="development",
        ),
    )


def make_wav():
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 16000)

    return buffer.getvalue()


def upload(audio=None, language="hi", key=TEST_KEY):
    if audio is None:
        audio = make_wav()

    return client.post(
        "/api/speech/transcribe",
        headers={"X-API-Key": key},
        files={"file": ("audio.wav", audio, "audio/wav")},
        data={"language": language},
    )


def test_valid_request():
    response = upload()

    assert response.status_code == 200
    assert response.json()["simulated"] is True
    assert response.json()["requires_confirmation"] is True
    assert response.json()["language"] == "hi"


def test_missing_key():
    assert upload(key="").status_code == 401


def test_invalid_key():
    assert upload(key="wrong").status_code == 401


def test_invalid_audio():
    assert upload(audio=b"invalid").status_code == 422


def test_unsupported_language():
    assert upload(language="fr").status_code == 422


def test_oversized_request():
    assert upload(
        audio=b"x" * (6 * 1024 * 1024)
    ).status_code == 413


def test_production_mock_disabled(monkeypatch):
    monkeypatch.setattr(
        speech,
        "get_settings",
        lambda: SimpleNamespace(
            speech_api_key=TEST_KEY,
            app_env="production",
        ),
    )

    assert upload().status_code == 503


def test_unexpected_form_field():
    response = client.post(
        "/api/speech/transcribe",
        headers={"X-API-Key": TEST_KEY},
        files={"file": ("audio.wav", make_wav(), "audio/wav")},
        data={"language": "hi", "extra": "unexpected"},
    )

    assert response.status_code == 422
