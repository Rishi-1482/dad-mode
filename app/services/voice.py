import base64
import io

from app.services.dad import client


def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    audio = io.BytesIO(audio_bytes)
    audio.name = filename

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio,
    )

    return transcript.text


def generate_speech(text: str) -> str:
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
        response_format="mp3",
    )

    return base64.b64encode(response.content).decode("utf-8")