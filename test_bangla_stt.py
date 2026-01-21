"""
Bangla Speech-to-Text using BanglaASR (Whisper fine-tuned for Bangla)
Outputs proper Bangla script (বাংলা)

Improved version with:
- Forced Bangla language output
- Repetition penalty to avoid loops
- Better audio processing with VAD (Voice Activity Detection)
- Error handling
"""

import sys
import warnings
import os

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
CHUNK_DURATION = 4  # seconds per chunk (increased for better context)
SILENCE_THRESHOLD = 0.02  # Minimum audio level to process
MIN_AUDIO_LEVEL = 0.005  # Minimum audio level for voice detection
MODEL_PATH = "models/stt/BanglaASR"

# Audio queue
audio_queue = queue.Queue()
is_recording = True


def audio_callback(indata, frames, time_info, status):
    """Callback for audio stream"""
    if is_recording:
        audio_queue.put(indata.copy())


def check_model():
    """Check if BanglaASR model exists"""
    if not os.path.exists(MODEL_PATH):
        print(f"❌ BanglaASR model not found at: {MODEL_PATH}")
        print("\n📥 To download the model:")
        print("   1. Install: pip install huggingface_hub")
        print("   2. Run: from huggingface_hub import snapshot_download")
        print("   3. Download: snapshot_download('Rakib/BanglaASR', local_dir='models/stt/BanglaASR')")
        return False
    return True


def load_model():
    """Load the BanglaASR model"""
    print("🔄 Loading BanglaASR model...")
    processor = WhisperProcessor.from_pretrained(MODEL_PATH)
    model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH)
    model.eval()
    
    # Set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"✅ Model loaded on {device.upper()}!")
    
    return processor, model, device


def is_valid_transcription(text):
    """Check if transcription is valid (not repetitive garbage)"""
    if not text or len(text) < 2:
        return False
    
    # Check for repetitive patterns
    words = text.split()
    if len(words) >= 3:
        # If more than 50% of words are the same, it's likely garbage
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        max_count = max(word_counts.values())
        if max_count > len(words) * 0.5:
            return False
    
    # Check for very long repeated characters
    for i in range(len(text) - 5):
        if text[i:i+3] == text[i+3:i+6]:
            return False
    
    return True


def transcribe_audio(audio, processor, model, device):
    """Transcribe audio to Bangla text"""
    # Normalize audio
    audio = audio / (np.abs(audio).max() + 1e-8)
    
    # Process audio
    inputs = processor(
        audio,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt"
    )
    
    # Move to device
    input_features = inputs.input_features.to(device)
    
    # Force Bangla language output
    forced_decoder_ids = processor.get_decoder_prompt_ids(
        language="bengali",
        task="transcribe"
    )
    
    # Generate Bangla text with repetition penalty
    with torch.no_grad():
        predicted_ids = model.generate(
            input_features,
            forced_decoder_ids=forced_decoder_ids,
            max_new_tokens=80,  # Limit output length
            repetition_penalty=1.5,  # Penalize repetitions
            no_repeat_ngram_size=3,  # Prevent 3-gram repetitions
            do_sample=False,  # Use greedy decoding
            num_beams=1,  # Faster with single beam
        )
    
    # Decode to Bangla script
    text = processor.batch_decode(
        predicted_ids,
        skip_special_tokens=True
    )[0].strip()
    
    return text


def has_speech(audio):
    """Simple voice activity detection"""
    # Calculate RMS energy
    rms = np.sqrt(np.mean(audio ** 2))
    
    # Check if there's enough energy for speech
    return rms > MIN_AUDIO_LEVEL


def main():
    """Main function for Bangla STT"""
    global is_recording
    
    print("\n" + "="*50)
    print("  🎤 Bangla Speech-to-Text (বাংলা STT)")
    print("="*50 + "\n")
    
    # Check model
    if not check_model():
        return
    
    # Load model
    processor, model, device = load_model()
    
    print("\n🎤 বাংলায় বলুন (Speak in Bangla)")
    print("   Press Ctrl+C to stop")
    print("="*50)
    
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
                    
                    # Check for voice activity
                    if not has_speech(audio):
                        continue
                    
                    # Calculate audio level
                    audio_level = np.abs(audio).max()
                    
                    # Skip silence
                    if audio_level < SILENCE_THRESHOLD:
                        continue
                    
                    # Transcribe
                    try:
                        text = transcribe_audio(audio, processor, model, device)
                        
                        # Validate and print
                        if text and is_valid_transcription(text):
                            print(f"🗣️ {text}")
                    except Exception as e:
                        # Silently skip transcription errors
                        continue
    
    except KeyboardInterrupt:
        is_recording = False
        print("\n\n👋 বিদায়! (Goodbye!)")


if __name__ == "__main__":
    main()
