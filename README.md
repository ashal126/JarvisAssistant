# Jarvis Voice Assistant

A simple voice-controlled desktop assistant written in Python.

## Current Features

- Wake word: `Jarvis`
- Opens common websites:
  - Google
  - Facebook
  - YouTube
  - LinkedIn
- Plays songs from `musicLibrary.py`
- Reads top news headlines with NewsAPI
- Sends fallback questions to OpenAI
- Uses offline `pyttsx3` text-to-speech

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure API keys:

```powershell
copy .env.example .env
```

Then open `.env` and paste your keys:

```text
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
```

`OPENAI_API_KEY` enables general AI questions. `NEWS_API_KEY` is only needed for the `news` command.

Run Jarvis:

```powershell
python main.py
```

## Example Commands

Say `Jarvis`, wait for the response, then say one of these:

```text
open google
open youtube
play skyfall
play best of me
news
what is coding?
exit
```

## Music Library

Songs are stored in `musicLibrary.py`:

```python
music = {
    "skyfall": "https://www.youtube.com/watch?v=DeumyOzKqgI",
}
```

Add more songs by adding new lower-case names and YouTube links.

## Notes

- `OPENAI_API_KEY` is required for AI responses. Jarvis loads it from `.env` automatically.
- `NEWS_API_KEY` is required for news.
- `OPENAI_MODEL` defaults to `gpt-4o-mini` and can be changed in `.env`.
- `NEWS_COUNTRY` defaults to `in` and can be changed in `.env`.
- Voice output uses `pyttsx3`, so Jarvis does not need `pygame`, `playsound`, or `gTTS`.
- If microphone setup fails on Windows, installing or fixing `pyaudio` is usually the first thing to check.

## Good Next Improvements

- Add reminders and notes with SQLite.
- Add weather commands.
- Add app-launch commands for local programs.
- Add a config file for wake word, news country, and preferred voice.
- Add tests for command parsing.
