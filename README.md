# Local Agent AI Voice Assistant

Talk to your computer. It talks back. Like your dad, but somehow *worse*.

Hit Enter → ramble into the mic → hit Enter again → Whisper hears you, GPT-4o-mini judges you, and TTS says it out loud with zero mercy.

## Setup

```bash
pip install -r requirements.txt
```

Add your OpenAI key to a `.env`:

```
OPENAPI_API_KEY=sk-your-key-here
```

## Run

```bash
python main.py
```

Then speak. Try not to take the feedback personally. (You will.)

## Pipeline

1. **Record** — your mic, your problems  
2. **Transcribe** — Whisper-1  
3. **Think** — GPT-4o-mini in "serious rude dad" mode  
4. **Speak** — TTS-1 (`alloy`) reads you the lecture  

No UI. No fluff. Just you, a microphone, and an AI dad who never asked for this either.
