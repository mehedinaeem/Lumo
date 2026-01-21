"""
Lumo BE - Bilingual Voice Assistant (Bangla/English)
Automatically detects language and responds in the same language.

Features:
- Bangla Speech-to-Text (BanglaASR)
- English Speech-to-Text (Vosk)
- Automatic language detection
- Responds in detected language
- Bangla TTS (gTTS) / English TTS (Piper)
"""

import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import sounddevice as sd
import numpy as np
import queue
import json
import subprocess
import time
import winsound
import threading
import itertools
from vosk import Model, KaldiRecognizer
from gpt4all import GPT4All

# Try to import Bangla TTS
try:
    from gtts import gTTS
    import pygame
    BANGLA_TTS_AVAILABLE = True
except ImportError:
    BANGLA_TTS_AVAILABLE = False
    print("⚠️ Bangla TTS not available. Install: pip install gtts pygame")

# Configuration
RATE = 16000
PIPER_PATH = "piper\\piper\\piper.exe"
ENGLISH_TTS_MODEL = "models\\tts\\en_US-amy-medium.onnx"
ENGLISH_STT_MODEL = "models/stt/vosk-model-small-en-us-0.15"

# Audio queue
audio_q = queue.Queue()
is_speaking = False


class Spinner:
    """Loading spinner for processing indication."""
    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
        self.thread = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def spin(self):
        for frame in itertools.cycle(self.frames):
            if not self.running:
                break
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def start(self, message=None):
        if message:
            self.message = message
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()


def audio_callback(indata, frames, time_info, status):
    """Callback for audio stream"""
    if not is_speaking:
        audio_q.put(bytes(indata))


def is_bangla_text(text):
    """Check if the text contains Bangla characters"""
    for char in text:
        if '\u0980' <= char <= '\u09FF':
            return True
    return False


def speak_english(text):
    """Speak English text using Piper TTS"""
    global is_speaking
    is_speaking = True
    
    # Clear audio queue
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except:
            pass
    
    # Escape special characters
    safe_text = text.replace('"', '').replace("'", "").replace('\n', ' ').replace('&', 'and')
    output_path = os.path.abspath("output_en.wav")
    
    result = subprocess.run(
        f'echo {safe_text} | {PIPER_PATH} --model {ENGLISH_TTS_MODEL} --output_file "{output_path}" --quiet',
        shell=True,
        capture_output=True
    )
    
    # Play audio
    try:
        winsound.PlaySound(output_path, winsound.SND_FILENAME)
    except:
        pass
    
    time.sleep(0.5)
    
    # Clear queue and reset
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except:
            pass
    
    is_speaking = False


def speak_bangla(text):
    """Speak Bangla text using gTTS"""
    global is_speaking
    
    if not BANGLA_TTS_AVAILABLE:
        print("⚠️ Bangla TTS not available")
        return
    
    is_speaking = True
    
    # Clear audio queue
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except:
            pass
    
    try:
        # Generate Bangla speech
        output_path = os.path.abspath("output_bn.mp3")
        tts = gTTS(text=text, lang='bn')
        tts.save(output_path)
        
        # Play with pygame
        pygame.mixer.init()
        pygame.mixer.music.load(output_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
    except Exception as e:
        print(f"⚠️ TTS Error: {e}")
    
    time.sleep(0.5)
    
    # Clear queue
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except:
            pass
    
    is_speaking = False


def speak(text, language="auto"):
    """Speak text in the appropriate language"""
    if language == "auto":
        language = "bn" if is_bangla_text(text) else "en"
    
    if language == "bn":
        speak_bangla(text)
    else:
        speak_english(text)


# Greeting messages
GREETING_BANGLA = "আমি লুমো, আপনার এ আই সহকারী। আজকে আমি কিভাবে আপনাকে সাহায্য করতে পারি?"
GREETING_ENGLISH = "Hello! I'm Lumo, your offline voice assistant. How can I help you today?"

# Greeting detection
ENGLISH_GREETINGS = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
BANGLA_GREETINGS = ["হ্যালো", "হাই", "হেই", "আসসালামু আলাইকুম", "সালাম", "নমস্কার"]


def is_greeting(text):
    """Check if text is a greeting"""
    text_lower = text.lower().strip()
    
    for g in ENGLISH_GREETINGS:
        if text_lower == g or text_lower.startswith(g + " "):
            return "en"
    
    for g in BANGLA_GREETINGS:
        if g in text:
            return "bn"
    
    return None


def main():
    """Main function for bilingual voice assistant"""
    global is_speaking
    
    spinner = Spinner()
    
    print("\n" + "="*55)
    print("  🤖 LUMO BE - Bilingual Voice Assistant")
    print("  🗣️ Speak in Bangla or English!")
    print("="*55)
    
    # Load English STT
    spinner.start("Loading English STT model")
    en_model = Model(ENGLISH_STT_MODEL)
    en_rec = KaldiRecognizer(en_model, RATE)
    spinner.stop()
    print("✅ English STT loaded!")
    
    # Load LLM
    spinner.start("Loading LLM")
    llm = GPT4All(
        model_name="orca-mini-3b-gguf2-q4_0.gguf",
        model_path="models/llm",
        allow_download=False
    )
    spinner.stop()
    print("✅ LLM loaded!")
    
    # Startup greeting
    print(f"\n🤖 Lumo: {GREETING_ENGLISH}")
    print(f"🤖 লুমো: {GREETING_BANGLA}")
    speak(GREETING_ENGLISH, "en")
    
    print("\n🎤 Listening... (say 'exit' to quit)")
    print("="*55 + "\n")
    
    conversation_history = []
    
    with sd.RawInputStream(
        samplerate=RATE, blocksize=8000,
        dtype='int16', channels=1, callback=audio_callback
    ):
        while True:
            if is_speaking:
                time.sleep(0.1)
                continue
            
            data = audio_q.get()
            if en_rec.AcceptWaveform(data):
                result = json.loads(en_rec.Result())
                text = result.get("text", "").strip()
                
                if not text or len(text) < 2:
                    continue
                
                # Exit command
                if text.lower() in ["exit", "quit", "stop", "goodbye", "bye"]:
                    print("👋 Goodbye! বিদায়!")
                    speak("Goodbye!", "en")
                    break
                
                print(f"🎤 You: {text}")
                
                # Detect language (English for Vosk, check for Bangla chars)
                is_bangla = is_bangla_text(text)
                
                # Check greeting
                greeting_lang = is_greeting(text)
                if greeting_lang:
                    if greeting_lang == "bn":
                        reply = GREETING_BANGLA
                    else:
                        reply = GREETING_ENGLISH
                else:
                    # Build prompt
                    conversation_history.append(f"User: {text}")
                    recent_history = conversation_history[-4:]
                    context = "\n".join(recent_history)
                    
                    if is_bangla:
                        prompt = f"""You are Lumo (লুমো), a helpful AI assistant.
The user is speaking in Bangla. Respond ONLY in Bangla script (বাংলা).
Keep your response concise (under 50 words).

{context}
লুমো:"""
                    else:
                        prompt = f"""You are Lumo, a helpful offline AI assistant.
Answer directly and helpfully. Be concise (under 50 words).

{context}
Lumo:"""
                    
                    spinner.start("Thinking" if not is_bangla else "ভাবছি")
                    reply = llm.generate(prompt, max_tokens=100)
                    reply = reply.strip()
                    spinner.stop()
                    
                    conversation_history.append(f"Lumo: {reply}")
                
                # Print and speak response
                print(f"🤖 Lumo: {reply}")
                speak(reply)
                
                # Reset recognizer
                en_rec.Reset()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! বিদায়!")
