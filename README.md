# 👩‍🏫 Teacher Sarah - AI English Tutor

**Teacher Sarah** is an advanced AI-powered English Tutor designed to help you practice your speaking, listening, and grammar through a beautiful Web Interface. 

Initially built as a Telegram/WhatsApp bot, the project has evolved into a fully interactive **Web Application** featuring real-time audio recording, vocabulary flashcards, and grammar analysis.

---

## 🚀 Features

- **🎙️ Dual Input Mode:** Practice your English by recording your voice directly in the browser or typing text messages.
- **🧠 Smart Grammar Feedback:** The AI (Gemini) analyzes your speech/text, identifies grammar mistakes, and provides clear, structured corrections and study tips.
- **🗣️ Native Voice (TTS):** Sarah replies with a natural-sounding English voice (powered by Edge-TTS), allowing you to practice your listening skills.
- **🖼️ Contextual Vocabulary Cards:** Automatically extracts a key vocabulary word from your conversation, generates a simple definition and example sentence, and fetches a beautiful, free image via the **Wikipedia API**.
- **📚 Pre-defined Study Topics:** A sleek sidebar containing study modules inspired by *Essential Grammar in Use* (e.g., Present Continuous, Past Simple) to guide your study sessions.
- **📥 Export to CSV:** Download your entire conversation history, including all grammar corrections and tips, for later review.
- **✨ Glassmorphism UI:** A modern, stunning, responsive interface built with vanilla HTML/CSS.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12, Flask
- **Frontend:** Vanilla HTML, CSS (Glassmorphism), JavaScript
- **AI Brain (LLM):** Google Gemini 3.1 Flash Lite (JSON Structured Outputs)
- **Voice Engine (TTS):** Edge-TTS (Free Microsoft Neural Voices - *Aria*)
- **Image Integration:** Wikipedia REST API (Free, no keys required)

---

## 📦 How to Run the Project

### Prerequisites
- Python 3.12+ installed
- Google Gemini API Key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/MATHEUS111JUNDIAI/bot-ingles.git
cd bot-ingles
```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

3. **Install the dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up Environment Variables:**
Create a `.env` file in the root directory and add your Gemini API key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

5. **Run the Application:**
```bash
python main.py
```

6. **Access the Web App:**
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 💡 How it works under the hood
1. The frontend captures audio via `MediaRecorder` or accepts text.
2. The payload is sent to Flask.
3. Flask sends the audio/text to **Gemini 3.1 Flash Lite** with a prompt enforcing a strict JSON output schema.
4. Gemini returns the transcription, a response, grammar errors, study suggestions, and a `vocab_word`.
5. The backend uses the `vocab_word` to fetch a thumbnail from the **Wikipedia API**.
6. The backend generates an audio file of Sarah's response using **Edge-TTS**.
7. The frontend renders the UI elements dynamically based on the JSON payload.