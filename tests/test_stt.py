import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# Correct path to VOSK model
model = Model("models/stt/vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

# Optional: print all devices to choose mic
#print(sd.query_devices())

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback,
    # device=1  # Uncomment and replace 1 with your mic index if default fails
):
    print("🎤 Speak now (Ctrl+C to stop)")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print("🗣️", result.get("text", ""))
