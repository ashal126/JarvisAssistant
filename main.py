import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
import os
from urllib.parse import quote_plus
import numpy as np
import sounddevice as sd

# pip install pocketsphinx

def load_env_file(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

load_env_file()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
NEWS_COUNTRY = os.getenv("NEWS_COUNTRY", "in")
SAMPLE_RATE = 16000

recognizer = sr.Recognizer()
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Text-to-speech is unavailable: {e}")
    engine = None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SITES = {
    "open google": "https://google.com",
    "open facebook": "https://facebook.com",
    "open youtube": "https://youtube.com",
    "open linkedin": "https://linkedin.com",
}

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

def has_pyaudio():
    try:
        sr.Microphone.get_pyaudio()
        return True
    except (AttributeError, ImportError):
        return False

USE_PYAUDIO = has_pyaudio()

def speak(text):
    print(f"Jarvis: {text}")
    if not engine:
        return

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech failed: {e}")

def get_browser():
    for chrome_path in CHROME_PATHS:
        if os.path.exists(chrome_path):
            return webbrowser.get(f'"{chrome_path}" %s')
    return webbrowser

def open_in_browser(url):
    try:
        get_browser().open(url)
    except webbrowser.Error:
        webbrowser.open(url)

def google_search_url(query):
    return f"https://www.google.com/search?q={quote_plus(query)}"

def web_quick_answer(query):
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=8,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Web answer request failed: {e}")
        return None

    data = response.json()
    answer = data.get("Answer") or data.get("AbstractText")
    if answer:
        return answer

    related_topics = data.get("RelatedTopics", [])
    for topic in related_topics:
        if isinstance(topic, dict) and topic.get("Text"):
            return topic["Text"]

    return None

def search_web(command):
    query = command.strip()
    search_prefixes = (
        "search google for ",
        "google search ",
        "search web for ",
        "search for ",
        "google ",
    )

    for prefix in search_prefixes:
        if query.lower().startswith(prefix):
            query = query[len(prefix):].strip()
            break

    if not query:
        speak("What should I search for?")
        return

    answer = web_quick_answer(query)
    if answer:
        speak(answer)
    else:
        speak("I could not find a quick answer, so I opened Google for you.")

    open_in_browser(google_search_url(query))

def aiProcess(command):
    if not openai_client:
        return "OpenAI is not configured yet. Paste your API key into the .env file as OPENAI_API_KEY=your_key_here, then restart Jarvis."

    completion = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Jarvis, a concise voice assistant. Answer general questions directly in 1-3 short sentences. "
                    "If the user asks a question with a false premise, briefly correct it before answering. "
                    "For example, NASA does not have a CEO; it is led by an Administrator. "
                    "If a question depends on very recent facts, say that the answer may need checking with a current source."
                ),
            },
            {"role": "user", "content": command}
        ]
    )

    return completion.choices[0].message.content

def open_site(command):
    for phrase, url in SITES.items():
        if phrase in command:
            open_in_browser(url)
            speak(f"Opening {phrase.replace('open ', '')}.")
            return True
    return False

def play_song(command):
    song = command.replace("play", "", 1).strip()

    if not song:
        speak("Which song should I play?")
        return

    link = musicLibrary.music.get(song)
    if not link:
        speak(f"I could not find {song} in your music library.")
        return

    open_in_browser(link)
    speak(f"Playing {song}.")

def read_news():
    if not NEWS_API_KEY:
        speak("News is not configured. Please set the NEWS_API_KEY environment variable.")
        return

    try:
        response = requests.get(
            f"https://newsapi.org/v2/top-headlines?country={NEWS_COUNTRY}&apiKey={NEWS_API_KEY}",
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"News request failed: {e}")
        speak("I could not fetch the news right now.")
        return

    articles = response.json().get("articles", [])
    if not articles:
        speak("I could not find any headlines right now.")
        return

    for article in articles[:5]:
        title = article.get("title")
        if title:
            speak(title)

def processCommand(command):
    original_command = command.strip()
    command = original_command.lower()

    if not command:
        speak("I did not catch that.")
    elif command in {"exit", "quit", "stop"}:
        speak("Goodbye.")
        raise SystemExit
    elif open_site(command):
        return
    elif command.startswith(("search google for ", "google search ", "search web for ", "search for ", "google ")):
        search_web(original_command)
    elif command.startswith("play"):
        play_song(command)
    elif "news" in command:
        read_news()
    else:
        if not openai_client:
            speak("OpenAI is not configured yet. I will search Google instead.")
            search_web(original_command)
            return

        try:
            speak(aiProcess(original_command))
        except Exception as e:
            print(f"AI request failed: {e}")
            speak("I could not process that with AI right now. I will search Google instead.")
            search_web(original_command)

def listen_audio(label, timeout=5, phrase_time_limit=5):
    print(label)

    if USE_PYAUDIO:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            return recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    duration = phrase_time_limit or timeout
    print(f"Recording for {duration} seconds with sounddevice...")
    recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    audio_bytes = np.asarray(recording, dtype=np.int16).tobytes()
    return sr.AudioData(audio_bytes, SAMPLE_RATE, 2)


if __name__ == "__main__":
    speak("Initializing Jarvis....")
    if not USE_PYAUDIO:
        print("PyAudio is not installed; using sounddevice for microphone input.")

    while True:
        # Listen for the wake word "Jarvis"
        # obtain audio from the microphone
        print("recognizing...")
        try:
            audio = listen_audio("Listening...", timeout=2, phrase_time_limit=2)
            word = recognizer.recognize_google(audio)
            if word.lower() == "jarvis":
                speak("Yes?")
                # Listen for command
                audio = listen_audio("Jarvis Active...", timeout=5, phrase_time_limit=8)
                command = recognizer.recognize_google(audio)

                processCommand(command)
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except Exception as e:
            print("Error; {0}".format(e))
