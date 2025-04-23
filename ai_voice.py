#!/usr/bin/env python3
import os
import time
import tempfile
import pyperclip
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
from pynput import keyboard

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def text_to_speech(text):
    """Convert text to speech using OpenAI API and play it"""
    try:
        # Create a temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_filename = temp_file.name
        temp_file.close()
        
        print(f"Converting to speech: {text[:50]}..." if len(text) > 50 else f"Converting to speech: {text}")
        
        # Generate speech using OpenAI API
        response = client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice="sage",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        # Save the audio to the temporary file using the recommended streaming method
        with open(temp_filename, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        # Play the audio using pydub
        audio = AudioSegment.from_mp3(temp_filename)
        play(audio)
        
        # Cleanup
        os.unlink(temp_filename)
        
        return True
    except Exception as e:
        print(f"Error converting text to speech: {e}")
        return False

def on_activate_hotkey():
    """Handle the keyboard shortcut activation"""
    print("Hotkey activated!")
    current_text = pyperclip.paste()
    if current_text.strip():
        text_to_speech(current_text)

def main():
    """Main function to set up keyboard shortcut and run the program"""
    print("AI Voice Assistant Running...")
    print("Press Command+Shift+V to speak the current clipboard contents")
    print("Press Ctrl+C in the terminal to exit") # pynput doesn't easily handle Ctrl+C exit detection
    print("------------------------------------------------------")

    # Define the hotkey combination (Command+Shift+V)
    # Note: Use keyboard.Key.cmd for Command key on macOS
    hotkey_combination = {
        keyboard.Key.cmd,
        keyboard.Key.shift,
        keyboard.KeyCode(char='v')
    }
    current_keys = set()

    def on_press(key):
        if key in hotkey_combination:
            current_keys.add(key)
            if all(k in current_keys for k in hotkey_combination):
                on_activate_hotkey()

    def on_release(key):
        try:
            current_keys.remove(key)
        except KeyError:
            pass

    # Start listening for keyboard events
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        # Keep the main thread alive
        listener.join()
    except KeyboardInterrupt:
        print("\nAI Voice Assistant stopping...")
        listener.stop()
        print("AI Voice Assistant stopped.")

if __name__ == "__main__":
    main() 