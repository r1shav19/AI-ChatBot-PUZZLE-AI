import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import requests
import edge_tts
import asyncio
import pygame
import pvporcupine
import pyaudio
import struct
import time
import webbrowser
import os

pygame.mixer.init()

# ---------------- WHISPER MODEL ---------------- #

model = WhisperModel("small", device="cpu", compute_type="int8")


# ---------------- TEXT TO SPEECH ---------------- #

async def generate_voice(text):
    filename = f"voice_{int(time.time())}.mp3"
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(filename)
    return filename


def speak(text):

    print("Puzzle:", text)

    filename = asyncio.run(generate_voice(text))

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# ---------------- AUDIO RECORD ---------------- #

def record_audio():

    duration = 5
    samplerate = 16000

    print("Listening...")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    wav.write("input.wav", samplerate, audio)


# ---------------- SPEECH TO TEXT ---------------- #

def transcribe():

    segments, _ = model.transcribe("input.wav")

    text = ""

    for segment in segments:
        text += segment.text

    text = text.strip().lower()

    if len(text) < 3:
        return ""

    return text


# ---------------- SYSTEM COMMANDS ---------------- #

def run_system_command(text):

    if "open chrome" in text:
        speak("Opening Chrome")
        webbrowser.open("https://google.com")
        return True

    if "open youtube" in text:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
        return True

    if "open spotify" in text:
        speak("Opening Spotify")
        os.system("start spotify")
        return True

    if "search google for" in text:
        query = text.replace("search google for", "")
        speak(f"Searching Google for {query}")
        webbrowser.open(f"https://google.com/search?q={query}")
        return True

    if "shutdown computer" in text:
        speak("Shutting down computer")
        os.system("shutdown /s /t 5")
        return True

    if "restart computer" in text:
        speak("Restarting computer")
        os.system("shutdown /r /t 5")
        return True

    return False


# ---------------- LLM ---------------- #

def ask_llm(prompt):

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()["response"]

    except:
        return "I cannot reach my brain right now."


# ---------------- WAKE WORD ---------------- #

ACCESS_KEY = "YOUR_PICOVOICE_ACCESS_KEY"

porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keyword_paths=["puzzle.ppn"]
)

pa = pyaudio.PyAudio()

audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)


def listen_for_wake_word():

    print("Waiting for wake word...")

    while True:

        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print("Wake word detected!")
            break


# ---------------- CONVERSATION MODE ---------------- #

def conversation_mode():

    last_interaction = time.time()

    while True:

        record_audio()

        user_text = transcribe()

        if user_text == "":
            continue

        print("You:", user_text)

        last_interaction = time.time()

        if "exit" in user_text:
            speak("Shutting down.")
            exit()

        if run_system_command(user_text):
            continue

        response = ask_llm(user_text)

        speak(response)

        # return to wake mode after inactivity
        if time.time() - last_interaction > 30:
            speak("Going back to sleep.")
            break


# ---------------- MAIN LOOP ---------------- #

speak("Puzzle online. What do you need?")

while True:

    listen_for_wake_word()

    speak("Yes?")

    conversation_mode()