
import base64
import hashlib

import requests
import streamlit as st
import os


def get_config(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


API_URL = get_config(
    "API_URL",
    "http://127.0.0.1:8000",
)

BACKEND_API_TOKEN = get_config(
    "BACKEND_API_TOKEN",
    "",
)

HEADERS = {
    "x-app-token": BACKEND_API_TOKEN,
}


st.set_page_config(
    page_title="Dad Mode",
    page_icon="👨",
    layout="centered",
)


st.title("👨 Dad Mode")
st.caption(
    "You know what you need to do. Dad just wants to know why you didn't do it."
)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = None

if "autoplay_audio" not in st.session_state:
    st.session_state.autoplay_audio = None


# -----------------------------
# Display conversation history
# -----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("audio"):
            audio_bytes = base64.b64decode(message["audio"])

            # Only autoplay the newest response.
            should_autoplay = (
                message["audio"] == st.session_state.autoplay_audio
            )

            st.audio(
                audio_bytes,
                format="audio/mp3",
                autoplay=should_autoplay,
            )


# Once the newest response has been rendered, clear the autoplay flag.
# This prevents the same response from automatically playing again
# on the next Streamlit rerun.
if st.session_state.autoplay_audio is not None:
    st.session_state.autoplay_audio = None


# -----------------------------
# Text chat
# -----------------------------

prompt = st.chat_input("Tell Dad what's going on...")


if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"message": prompt},
            headers=HEADERS,
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        dad_response = data["response"]
        route = data.get("route", "normal")
        sources = data.get("sources", [])

        tool_calls = data.get("tool_calls", [])

        if route == "rag":
            st.caption("📚 Dad used your knowledge base")

        elif route == "web":
            st.caption("🌐 Dad searched the web")

        elif route == "hybrid":
            st.caption("🧠 Dad used your knowledge base + web")

        elif route == "normal":
            st.caption("💬 Dad answered directly")
        
        if tool_calls:
            st.caption(
                "Tools: " + ", ".join(tool_calls)
            )

        if sources:
            st.markdown("### Sources")

            for source in sources:

                if isinstance(source, str):
                    st.write(f"- {source}")

                else:
                    title = source.get("title", "Source")
                    url = source.get("url", "")

                    if url:
                        st.markdown(
                            f"- [{title}]({url})"
                        )

    except requests.RequestException as e:
        dad_response = f"Dad's brain is offline: {e}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": dad_response,
        }
    )

    with st.chat_message("assistant"):
        st.write(dad_response)


# -----------------------------
# Voice input
# -----------------------------

st.divider()

st.subheader("🎤 Talk to Dad")

audio_value = st.audio_input(
    "Record a voice message",
    sample_rate=16000,
)


if audio_value is not None:

    audio_bytes = audio_value.getvalue()

    # Prevent Streamlit reruns from processing the same recording repeatedly.
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()

    if audio_hash != st.session_state.processed_audio:

        st.session_state.processed_audio = audio_hash

        try:
            with st.spinner("Dad is thinking..."):

                response = requests.post(
                    f"{API_URL}/voice",
                    files={
                        "file": (
                            audio_value.name or "recording.wav",
                            audio_bytes,
                            "audio/wav",
                        )
                    },
                    headers=HEADERS,
                    timeout=120,
                )

                response.raise_for_status()
                data = response.json()

            transcript = data["transcript"]
            dad_response = data["response"]
            audio_base64 = data["audio_base64"]

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": transcript,
                }
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": dad_response,
                    "audio": audio_base64,
                }
            )

            # Tell the next render to autoplay this response.
            st.session_state.autoplay_audio = audio_base64

            st.rerun()

        except requests.RequestException as e:
            st.error(f"Voice request failed: {e}")
