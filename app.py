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
from datetime import datetime

load_dotenv()
st.set_page_config(layout="wide")

MEMORY_FILE = "thinkflow_memory.json"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_resource
def load_model():
    return WhisperModel("base.en", device="cpu", compute_type="int8")

model = load_model()

# Initialize session state
defaults = {
    "resources": [],
    "notes": "",
    "generate_pressed": False,
    "llm_response": "",
    "transcribed_text": "",
    "memory": [],
    "current_idea_index": None
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Load memory from file
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        st.session_state.memory = json.load(f)

# ==== Sidebar memory system ====
st.sidebar.title("💾 Saved Ideas")

# Button to start a new idea
if st.sidebar.button("➕ New Idea"):
    st.session_state.transcribed_text = ""
    st.session_state.llm_response = ""
    st.session_state.notes = ""
    st.session_state.resources = []
    st.session_state.generate_pressed = False
    st.session_state.current_idea_index = None

# List of saved ideas
if st.session_state.memory:
    for idx, idea in enumerate(st.session_state.memory[::-1]):
        real_index = len(st.session_state.memory) - idx - 1
        label = idea.get("transcript", "").split("\n")[0][:40] or f"Idea {real_index + 1}"
        
        col_a, col_b = st.sidebar.columns([5, 1])
        with col_a:
            if st.button(label, key=f"mem_{real_index}"):
                selected = st.session_state.memory[real_index]
                st.session_state.transcribed_text = selected["transcript"]
                st.session_state.llm_response = selected["response"]
                st.session_state.notes = selected.get("notes", "")
                st.session_state.resources = selected.get("resources", [])
                st.session_state.generate_pressed = True
                st.session_state.current_idea_index = real_index

        with col_b:
            if st.button("🗑️", key=f"del_{real_index}"):
                st.session_state.memory.pop(real_index)
                with open(MEMORY_FILE, "w") as f:
                    json.dump(st.session_state.memory, f, indent=2)
                st.rerun()

# ==== Main App ====
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

            cleaned_response = response.choices[0].message.content.strip()
            st.session_state.llm_response = cleaned_response
            st.session_state.generate_pressed = True

            # Save to memory
            label = new_transcript.strip().split("\n")[0][:50] or f"Idea {len(st.session_state.memory)+1}"
            new_idea = {
                "timestamp": datetime.now().isoformat(),
                "transcript": new_transcript,
                "response": cleaned_response,
                "notes": "",
                "resources": [],
                "label": label
            }
            st.session_state.memory.append(new_idea)
            st.session_state.current_idea_index = len(st.session_state.memory) - 1

            with open(MEMORY_FILE, "w") as f:
                json.dump(st.session_state.memory, f, indent=2)
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.generate_pressed:
    with col1:
        st.subheader("📄 Transcribed Text")
        st.text_area("Transcript", value=st.session_state.transcribed_text, height=200, disabled=True)

        st.subheader("🗒️ Add Notes")
        st.session_state.notes = st.text_area("Notes", value=st.session_state.notes, height=100, key="notes_box")

        st.subheader("🔗 Resources")
        new_link = st.text_input("Add a Resource URL")
        if new_link and new_link not in st.session_state.resources:
            st.session_state.resources.append(new_link)

        for url in st.session_state.resources:
            st.markdown(f"- [{url}]({url})")

        def fetch_url_content(url):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.content, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                return soup.get_text(separator=" ", strip=True)[:1500]
            except Exception as e:
                return f"[Could not fetch {url}: {e}]"

        st.subheader("🔄 Expand Idea")
        if st.button("✨ Expand"):
            with col2:
                web_context = "\n\n".join([fetch_url_content(url) for url in st.session_state.resources])
                expansion_prompt = f"""
    I want you to act like an expert Planner. If anyone has an idea, a task or a query, you lay out a detailed plan on how to tackle it, 
    how to complete it or how to solve it step by step. Pay Equal attention to the Transcript, user Notes and deep attention to the resource:

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

                # Update memory
                idx = st.session_state.current_idea_index
                if idx is not None:
                    st.session_state.memory[idx]["notes"] = st.session_state.notes
                    st.session_state.memory[idx]["resources"] = st.session_state.resources
                    st.session_state.memory[idx]["response"] = st.session_state.llm_response

                    with open(MEMORY_FILE, "w") as f:
                        json.dump(st.session_state.memory, f, indent=2)
                        st.rerun()


        with col2:
            st.subheader("🤖 LLM Response")
            cleaned = re.sub(r"^```[a-z]*\n?|```$", "", st.session_state.llm_response.strip(), flags=re.IGNORECASE | re.MULTILINE)
            st.markdown(cleaned)
