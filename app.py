import streamlit as st
import io
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from faster_whisper import WhisperModel
from streamlit_mic_recorder import mic_recorder
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(layout="wide")

LLM_OUTPUT_FILE = "llm_output.json"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_resource
def load_model():
    return WhisperModel("base.en", device="cpu", compute_type="int8")

model = load_model()

if "resources" not in st.session_state:
    st.session_state.resources = []

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "generate_pressed" not in st.session_state:
    st.session_state.generate_pressed = False

if "llm_response" not in st.session_state:
    st.session_state.llm_response = ""

if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

st.title("ThinkFlow: Voice-to-Idea")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("🔴 Record & Transcribe")
    audio_data = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="🛑 Stop & Process",
        just_once=True,
        use_container_width=True,
        key="recorder"
    )

    if audio_data:
        wav_bytes = audio_data["bytes"]
        st.audio(wav_bytes, format='audio/wav')

        try:
            segments, _ = model.transcribe(io.BytesIO(wav_bytes), language="en")
            new_transcript = "".join(seg.text + " " for seg in segments).strip()

            st.session_state.transcribed_text = new_transcript

            prompt = f"""I want you to act like an expert Planner. You are a planner of all things. 
If anyone has an idea, a task or a query, you lay out a detailed plan on how to tackle it, 
how to complete it or how to solve it step by step. You are very knowledgeable and know a lot about everything. 
The person has an idea/task they want to realize as follows: {new_transcript}. 
Give an extremely detailed plan in MARKDOWN only."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=None,
            )

            result = {
                "transcript": new_transcript,
                "response": response.choices[0].message.content.strip()
            }

            with open(LLM_OUTPUT_FILE, "w") as f:
                json.dump(result, f, indent=2)

            st.session_state.llm_response = result["response"]
            st.session_state.generate_pressed = True

        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.generate_pressed:
    with col1:
        st.subheader("📄 Transcribed Text")
        st.text_area("Transcript", value=st.session_state.transcribed_text, height=200, disabled=True)

    with col2:
        st.subheader("🤖 LLM Response")
        cleaned_response = re.sub(r"^```[a-z]*\n?|```$", "", st.session_state.llm_response.strip(), flags=re.IGNORECASE | re.MULTILINE)
        st.markdown(cleaned_response)

        st.subheader("🗒️ Add Notes")
        st.session_state.notes = st.text_area("Notes", value=st.session_state.notes, height=100, key="notes_box")

        st.subheader("🔗 Resources")
        new_link = st.text_input("Add a Resource URL")
        if new_link and new_link not in st.session_state.resources:
            st.session_state.resources.append(new_link)

        for url in st.session_state.resources:
            st.markdown(f"- [{url}]({url})")

        # Helper to fetch page content with headers
        def fetch_url_content(url):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/110.0.0.0 Safari/537.36"
                }
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.content, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                return soup.get_text(separator=" ", strip=True)[:1500]
            except Exception as e:
                return f"[Could not fetch {url}: {e}]"

        st.subheader("🔄 Expand Idea")
        if st.button("✨ Expand with LLM"):
            web_context = "\n\n".join([fetch_url_content(url) for url in st.session_state.resources])
            expansion_prompt = f"""
I want you to act like an expert Planner. You are a planner of all things. 
If anyone has an idea, a task or a query, you lay out a detailed plan on how to tackle it, 
how to complete it or how to solve it step by step. You are very knowledgeable and know a lot about everything. 
The person has an idea/task they want to realize as follows:

## Transcript:
{st.session_state.transcribed_text}

## User Notes:
{st.session_state.notes}

## Resource Content:
{web_context}

Give an extremely detailed plan in MARKDOWN only.
"""
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": expansion_prompt}],
                max_tokens=None,
            )
            st.session_state.llm_response = response.choices[0].message.content.strip()
            st.rerun()