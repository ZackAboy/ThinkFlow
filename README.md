# 🧠 ThinkFlow: Voice-to-Idea
**ThinkFlow** is an AI-powered idea management and planning assistant. It captures your spontaneous voice-recorded ideas, transcribes them in real-time, and transforms them into structured, actionable plans using LLMs (Large Language Models). ThinkFlow lets you expand your ideas with notes, web resources, and iterative refinement.

---

## 🚀 Features

- 🎙️ **Real-Time Voice Transcription** powered by [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper).
- 🤖 **AI-Powered Planning** via GPT-4o (OpenAI).
- 📚 **Memory Sidebar**: Save, access, edit, or delete past ideas.
- 📝 **Notes & Annotations**: Easily add context or additional thoughts.
- 🔗 **Resource Integration**: Add links and automatically extract web content to enrich planning.
- ✨ **Idea Expansion**: Deepen ideas by merging your notes, transcript, and web resources.
- 🔄 **Persistent Local Storage** using JSON for privacy and simplicity.

---

## 📹 Demo

![Demo GIF](demo/demo.gif)  
[Demo Video](https://youtu.be/rvtyZgJoR1E)

---

## 🛠️ Tech Stack

| Component      | Technology/Library                                             |
|----------------|----------------------------------------------------------------|
| **UI**         | [Streamlit](https://streamlit.io/)                             |
| **Voice Capture**  | [streamlit-mic-recorder](https://pypi.org/project/streamlit-mic-recorder/) |
| **Transcription**  | [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)    |
| **AI Planning**    | [OpenAI GPT-4o](https://openai.com/)                           |
| **Web Scraping**   | `requests`, `BeautifulSoup4`                                   |
| **Storage**        | JSON-based (`thinkflow_memory.json`)                           |
| **Environment**    | `.env` with [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## 🧑‍💻 How to Run Locally

1. **Clone the Repository**

        git clone https://github.com/yourusername/thinkflow.git
        cd thinkflow

2. **Set up Python Environment**

        python -m venv venv
        source venv/bin/activate  # Linux/Mac
        venv\Scripts\activate     # Windows

3. **Install Dependencies**

        pip install -r requirements.txt

4. **Add OpenAI API Key**

   Create a `.env` file in the root folder with the following content:

        OPENAI_API_KEY=your-api-key

5. **Run the App**

        streamlit run app.py

---

## 📂 Project Structure

        ThinkFlow/
        ├── app.py                   # Streamlit Application
        ├── thinkflow_memory.json    # Local Idea Storage
        ├── .env                     # OpenAI API Key
        ├── requirements.txt         # Python dependencies
        └── README.md                # This documentation

---

## 📖 Use Cases

- Quick capturing of spontaneous ideas.
- Rapid brainstorming and structured planning.
- Research assistance by linking and processing web resources.
- Organizing project tasks and personal goals through voice.

---

## 🛡️ Privacy

ThinkFlow stores all data locally in `thinkflow_memory.json`. Your ideas remain private and secure, with no external storage or cloud upload unless explicitly added.

---

## 🔮 Future Improvements

- Tagging and advanced search functionalities.
- Optional cloud synchronization (Google Drive, Dropbox).
- Integration with task management tools (Notion, Trello).
- Mobile compatibility enhancements.

---

## 📜 License

MIT License. Feel free to use, adapt, and extend the project.

---

## 👤 Author

**Sahil Gujral**  
- 🎓 CS Master's Student @ USC 
