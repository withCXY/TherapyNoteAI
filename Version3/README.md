# Therapy Note Assistant

A Streamlit-based application that helps therapists record, transcribe, and analyze therapy sessions. The app provides real-time voice recording, audio file upload capabilities, and generates summaries and reports using AI.

## Features

- Real-time voice recording with visual feedback
- Audio file upload support (MP3, WAV, M4A)
- Automatic transcription using OpenAI's Whisper API
- AI-powered summary generation
- Downloadable session reports
- Search functionality for previous conversations

## Setup

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/therapy-note-assistant.git
cd therapy-note-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## License

MIT License 