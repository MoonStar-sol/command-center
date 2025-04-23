# AI Voice Assistant

This script monitors your clipboard and uses OpenAI's Text-to-Speech API to read aloud any text you copy.

## Setup

1. Ensure you have Python 3.6+ installed
2. Install required packages:
```
pip install pyperclip openai python-dotenv pygame
```
3. Make sure your `.env` file contains your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

1. Run the script:
```
python ai_voice.py
```
2. Copy any text (Cmd+C/Ctrl+C) that you want to be read aloud
3. The script will automatically detect the clipboard change and speak the text
4. To stop the script, press Ctrl+C in the terminal window

## Voice Options

You can change the voice by editing the script. OpenAI offers these voice options:
- `alloy`: Neutral voice (default)
- `echo`: Balanced voice
- `fable`: Expressive voice
- `onyx`: Deep, authoritative voice
- `nova`: Clear voice
- `shimmer`: Soft, warm voice

To change the voice, edit the `voice` parameter in the `text_to_speech` function.

For higher quality audio, you can also change `tts-1` to `tts-1-hd` in the `model` parameter, but this will use more API credits.

## Troubleshooting

- If you hear no audio, check your system's sound settings
- If you get API errors, verify your OpenAI API key is correct and has sufficient credits
- If the script crashes, ensure all dependencies are properly installed 