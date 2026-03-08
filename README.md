# Puzzle AI Assistant

Puzzle AI is a local voice-controlled AI assistant similar to Jarvis.
(note: Users must provide their own Picovoice access key.)
## Features

- Wake word detection ("Puzzle")
- Speech recognition using Whisper
- Local LLM responses using Ollama (Mistral)
- Text-to-speech using Edge TTS
- Voice conversation mode
- System automation commands

## Example Commands

Puzzle open chrome  
Puzzle search google for Tokyo Ghoul  
Puzzle open youtube  
Puzzle shutdown computer

## Tech Stack

- Python
- Whisper
- Ollama
- Porcupine Wake Word Engine
- Edge TTS
- Pygame

## Architecture

Wake Word → Porcupine  
Speech Recognition → Whisper  
LLM → Ollama (Mistral)  
Speech Output → Edge TTS  
Audio Playback → Pygame

## Future Improvements

- Memory system
- Smart home control
- Plugin system
- GPU acceleration