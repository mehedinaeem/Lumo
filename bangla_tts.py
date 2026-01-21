"""
Lumo - Bangla Text-to-Speech Module
Provides Bangla TTS functionality using gTTS (Google Text-to-Speech)

Usage:
    from bangla_tts import speak_bangla
    speak_bangla("আমি লুমো, আপনার এ আই সহকারী।")
"""

import sys
import os

# Fix Windows console encoding for Bangla text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from gtts import gTTS
import pygame
import tempfile


def speak_bangla(text, save_file=None, play_audio=True):
    """
    Convert Bangla text to speech and optionally play it
    
    Args:
        text: Bangla text to convert to speech
        save_file: Optional path to save the audio file (MP3)
        play_audio: Whether to play the audio (default: True)
    
    Returns:
        str: Path to the generated audio file
    """
    # Use temp file if no save path provided
    if save_file is None:
        temp_dir = tempfile.gettempdir()
        save_file = os.path.join(temp_dir, "lumo_bangla_output.mp3")
    
    # Generate Bangla speech using gTTS
    tts = gTTS(text=text, lang='bn')  # 'bn' = Bengali/Bangla
    tts.save(save_file)
    
    # Play audio if requested
    if play_audio:
        play_mp3(save_file)
    
    return save_file


def play_mp3(file_path):
    """Play an MP3 file using pygame"""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    
    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.quit()


# Demo / Test
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🔊 Bangla Text-to-Speech Demo")
    print("="*50 + "\n")
    
    # Test sentences
    test_texts = [
        "আমি লুমো, আপনার অফলাইন এ আই সহকারী।",
        "আপনাকে স্বাগতম।",
        "আজকে আমি কিভাবে আপনাকে সাহায্য করতে পারি?",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"--- Test {i} ---")
        print(f"📝 Text: {text}")
        print("🔊 Speaking...")
        speak_bangla(text)
        print("✅ Done!\n")
    
    # Interactive mode
    print("\n" + "="*50)
    print("  💬 Interactive Mode")
    print("="*50)
    
    while True:
        try:
            user_text = input("\nবাংলায় টাইপ করুন (Enter Bangla text): ").strip()
            if user_text.lower() in ['exit', 'quit', 'bye', 'বিদায়']:
                print("\n👋 বিদায়!")
                break
            if user_text:
                speak_bangla(user_text)
        except KeyboardInterrupt:
            print("\n\n👋 বিদায়!")
            break
