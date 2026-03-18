"""
Lumo - Bangla Text-to-Speech Test Script
Tests multiple TTS approaches for Bangla language
"""

import sys
import os

# Fix Windows console encoding for Bangla text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def test_gtts_bangla(text, output_file="bangla_output_gtts.mp3"):
    """
    Test gTTS (Google Text-to-Speech) for Bangla
    Note: Requires internet connection
    """
    try:
        from gtts import gTTS
        import pygame
        
        print(f"📝 Text: {text}")
        print("🔄 Generating speech with gTTS...")
        
        # Generate Bangla speech
        tts = gTTS(text=text, lang='bn')  # 'bn' = Bengali/Bangla
        tts.save(output_file)
        
        print(f"✅ Speech saved to: {output_file}")
        
        # Play the audio
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        print("✅ Playback complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Install with: pip install gtts pygame")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_bangla_tts_library(text, output_file="bangla_output.wav"):
    """
    Test BanglaTTS library (offline)
    """
    try:
        from bangla_tts import BanglaTTS
        import winsound
        
        print(f"📝 Text: {text}")
        print("🔄 Generating speech with BanglaTTS...")
        
        # Initialize BanglaTTS
        tts = BanglaTTS()
        
        # Generate speech (female voice by default)
        tts.synthesize(text, output_file, voice='female')
        
        print(f"✅ Speech saved to: {output_file}")
        print("🔊 Playing audio...")
        
        # Play the audio
        winsound.PlaySound(output_file, winsound.SND_FILENAME)
        print("✅ Playback complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Install with: pip install bangla-tts")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_pyttsx3_bangla(text):
    """
    Test pyttsx3 for Bangla (requires Bangla voice installed on system)
    Note: Works offline if Bangla voice is available
    """
    try:
        import pyttsx3
        
        print(f"📝 Text: {text}")
        print("🔄 Checking available voices...")
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Look for Bangla voice
        bangla_voice = None
        print("\n📋 Available voices:")
        for voice in voices:
            print(f"   - {voice.name} ({voice.languages})")
            if 'bangla' in voice.name.lower() or 'bengali' in voice.name.lower() or 'bn' in str(voice.languages).lower():
                bangla_voice = voice.id
                
        if bangla_voice:
            engine.setProperty('voice', bangla_voice)
            print(f"\n✅ Found Bangla voice!")
        else:
            print("\n⚠️ No Bangla voice found. Using default voice.")
            print("   Install Bangla voice on Windows: Settings > Time & Language > Speech")
        
        print("🔊 Speaking...")
        engine.say(text)
        engine.runAndWait()
        print("✅ Playback complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def speak_bangla(text, output_file="bangla_output.mp3", method="gtts"):
    """
    Main function to speak Bangla text
    
    Args:
        text: Bangla text to speak
        output_file: Output audio file path
        method: 'gtts' (online), 'bangla_tts' (offline), or 'pyttsx3' (offline)
    """
    if method == "gtts":
        return test_gtts_bangla(text, output_file)
    elif method == "bangla_tts":
        return test_bangla_tts_library(text, output_file.replace('.mp3', '.wav'))
    elif method == "pyttsx3":
        return test_pyttsx3_bangla(text)
    else:
        print(f"❌ Unknown method: {method}")
        return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🔊 LUMO - Bangla Text-to-Speech Test")
    print("="*50 + "\n")
    
    # Test sentences in Bangla
    test_texts = [
        "আমি লুমো, আপনার অফলাইন এ আই সহকারী।",
        "আপনাকে স্বাগতম।",
        "আজকে আমি কিভাবে আপনাকে সাহায্য করতে পারি?",
    ]
    
    print("📌 Available TTS Methods:")
    print("   1. gTTS (Google TTS) - Online, good quality")
    print("   2. BanglaTTS - Offline, open-source")
    print("   3. pyttsx3 - Offline, requires system Bangla voice")
    print()
    
    # Test gTTS (most reliable for Bangla)
    print("\n" + "-"*50)
    print("  Testing gTTS (Google Text-to-Speech)")
    print("-"*50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Test {i} ---")
        test_gtts_bangla(text, f"bangla_test_{i}.mp3")
    
    # Interactive mode
    print("\n" + "="*50)
    print("  💬 Interactive Mode (type 'exit' to quit)")
    print("="*50)
    
    while True:
        try:
            user_text = input("\nবাংলায় টাইপ করুন (Enter Bangla text): ").strip()
            if user_text.lower() in ['exit', 'quit', 'bye', 'বিদায়']:
                print("\n👋 বিদায়! (Goodbye!)")
                break
            if user_text:
                speak_bangla(user_text, method="gtts")
        except KeyboardInterrupt:
            print("\n\n👋 বিদায়! (Goodbye!)")
            break
