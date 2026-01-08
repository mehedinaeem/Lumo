import sounddevice as sd
import queue, json, subprocess, time, winsound, os
from vosk import Model, KaldiRecognizer
from gpt4all import GPT4All

print("Imports done")

RATE = 16000
audio_q = queue.Queue()
is_speaking = False

def audio_callback(indata, frames, time_info, status):
    if not is_speaking:
        audio_q.put(bytes(indata))

# STT
print("Loading VOSK model...")
model = Model("models/stt/vosk-model-small-en-us-0.15")
print("VOSK model loaded. Creating recognizer...")
rec = KaldiRecognizer(model, RATE)
print("Recognizer created.")

# LLM
print("Loading GPT4All model...")
try:
    llm = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", allow_download=False)
    print("GPT4All model loaded (no download).")
except Exception as e:
    print(f"GPT4All load failed with allow_download=False: {e}")
    print("Retrying with default settings (might download)...")
    llm = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
    print("GPT4All model loaded.")

conversation_history = []

def speak(text):
    # (Simplified for debug)
    pass

print("[*] LUMO is listening... (DEBUG MODE)")
