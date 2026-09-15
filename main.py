import sounddevice as sd
import soundfile as sf
import tempfile
import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAPI_API_KEY = os.getenv("OPENAPI_API_KEY")

SAMPLE_RATE = 160000
MAX_DURATION = 30
SAMPLES = SAMPLE_RATE * MAX_DURATION

client = openai.OpenAI(api_key=OPENAPI_API_KEY)

def record_audio():

    input("Press Enter to start recording...")
    print("Recording... Press enter to stop")

    audio_data = sd.rec(SAMPLES, SAMPLE_RATE, channels=1, dtype='float64')
    input()
    sd.stop()
    print("Recording stopped")
    temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(temp.name, audio_data, SAMPLE_RATE)
    print(f"Audio saved to {temp.name}")

    return temp.name

def transcribe(audio_path):
    with open(audio_path, "rb") as audio_file:
        output = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )
    return output

def think(text):
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="You are a helpful AI voice assistant who talks like my serious Dad in a rude way.",
        input=text,
    )
    return response.output_text

def speak(text):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        input=text,
        voice='alloy',
    ) as response:
        response.stream_to_file("response.mp3")
    data, sr = sf.read("response.mp3") # sr is sample rate
    sd.play(data, sr)
    sd.wait()
    os.remove("response.mp3")


audio = record_audio()
text = transcribe(audio)
response = think(text)
speak(response)
print(text)
print(response)