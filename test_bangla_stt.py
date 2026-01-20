"""
Bangla Speech-to-Text using BanglaASR (Whisper fine-tuned for Bangla)
Outputs proper Bangla script (বাংলা)
"""

import sys
import warnings

# Suppress transformer warnings
warnings.filterwarnings("ignore")

# Fix Windows console encoding for Bangla text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import sounddevice as sd
import numpy as np
import queue
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import logging

# Suppress transformers logging
logging.getLogger("transformers").setLevel(logging.ERROR)

# Configuration
SAMPLE_RATE = 16000
CHUNK_DURATION = 3  # seconds per chunk
MODEL_PATH = "models/stt/BanglaASR"

# Audio queue
audio_queue = queue.Queue()
is_recording = True

def audio_callback(indata, frames, time_info, status):
    """Callback for audio stream"""
    if is_recording:
        audio_queue.put(indata.copy())

# Load BanglaASR model
print("🔄 Loading BanglaASR model...")
processor = WhisperProcessor.from_pretrained(MODEL_PATH)
model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH)
model.eval()
print("✅ Model loaded!")

print("\n🎤 বাংলায় বলুন (Ctrl+C to stop)")
print("=" * 40)

try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32',
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * 0.1)
    ):
        audio_buffer = []
        samples_needed = int(SAMPLE_RATE * CHUNK_DURATION)
        
        while True:
            chunk = audio_queue.get()
            audio_buffer.append(chunk.flatten())
            
            total_samples = sum(len(c) for c in audio_buffer)
            
            if total_samples >= samples_needed:
                # Combine audio
                audio = np.concatenate(audio_buffer)
                audio_buffer = []
                
                # Skip silence
                if np.abs(audio).max() < 0.01:
                    continue
                
                # Process with BanglaASR
                inputs = processor(
                    audio,
                    sampling_rate=SAMPLE_RATE,
                    return_tensors="pt"
                )
                
                # Generate Bangla text
                with torch.no_grad():
                    predicted_ids = model.generate(
                        inputs.input_features,
                        attention_mask=torch.ones(inputs.input_features.shape[:2], dtype=torch.long)
                    )
                
                # Decode to Bangla script
                text = processor.batch_decode(
                    predicted_ids,
                    skip_special_tokens=True
                )[0].strip()
                
                if text:
                    print(f"🗣️ {text}")

except KeyboardInterrupt:
    is_recording = False
    print("\n\n👋 বিদায়!")
