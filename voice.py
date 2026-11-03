"""SOLARIS Advanced Voice System: STT, TTS, wake word, and interaction modes."""
import asyncio
import config
import os

# Voice style definitions
VOICE_STYLES = {
    "A": {
        "id": "en-US-JennyNeural",
        "name": "Natural Conversational",
        "description": "Human-like, warm, conversational voice.",
        "gender": "female",
    },
    "B": {
        "id": "en-US-Sara-Natural",
        "name": "Deep Cinematic",
        "description": "Deep, SOLARIS/JARVIS-inspired cinematic voice.",
        "gender": "male",
    },
}

# Default settings
DEFAULT_VOICE_STYLE = "A"
DEFAULT_SPEED = 1.0
DEFAULT_MICROPHONE = None


class VoiceManager:
    def __init__(self):
        self.voice_style = DEFAULT_VOICE_STYLE
        self.speed = DEFAULT_SPEED
        self.microphone = DEFAULT_MICROPHONE
        self.is_listening = False
        self.is_speaking = False
        self.listener_task = None
        self.tts_task = None

    async def start_listening(self):
        """Start push-to-toggle or hotkey listening."""
        if self.is_listening:
            return
        self.is_listening = True
        # In a real implementation, this would set up speech recognition
        # For now, we just mark the state change
        config.VOICE_STATE = "listening"

    async def stop_listening(self):
        """Stop listening."""
        self.is_listening = False
        config.VOICE_STATE = "idle"

    async def process_speech(self, text):
        """Process recognized speech."""
        if not text or not text.strip():
            return
        text = text.strip()

        # Check for wake word
        if text.lower().startswith('hey solaris'):
            text = text[12:].strip()
            await self.activate(text)
        else:
            await self.handle_command(text)

    async def activate(self, text=""):
        """Activate SOLARIS with optional command."""
        config.VOICE_STATE = "listening"

        if text:
            await self.handle_command(text)
        else:
            # Just listen for further input
            pass

    async def handle_command(self, text):
        """Handle a voice command."""
        # Simple command routing
        text_lower = text.lower()

        if any(word in text_lower for word in ['hello', 'hi', 'hey']):
            await self.speak("Hello! How can I help you today?")
        elif 'thank' in text_lower:
            await self.speak("You're welcome!")
        elif 'how are you' in text_lower:
            await self.speak("I'm doing well, thank you for asking!")
        elif 'time' in text_lower:
            from datetime import datetime
            await self.speak(f"The current time is {datetime.now().strftime('%I:%M %p')}")
        else:
            # Pass to AI brain
            await self.speak("I'm thinking about that...")
            # Could integrate with brain.py here

    async def speak(self, text, voice_style=None):
        """Text-to-speech with specified voice style."""
        if voice_style is None:
            voice_style = self.voice_style

        if self.is_speaking:
            # Wait for current speech to finish
            await asyncio.sleep(0.5)

        self.is_speaking = True
        config.VOICE_STATE = "speaking"

        try:
            # Use edge-tts for speech synthesis
            voice_id = VOICE_STYLES.get(voice_style, VOICE_STYLES["A"])["id"]

            # In a real implementation, this would use edge_tts
            # For now, just update the state
            await asyncio.sleep(0.1)  # Simulate TTS

            # Notify that speech is done
            self.is_speaking = False
            config.VOICE_STATE = "idle"
        except Exception as e:
            self.is_speaking = False
            config.VOICE_STATE = "idle"
            raise e

    def set_voice_style(self, style_id):
        """Set the voice style (A or B)."""
        if style_id in VOICE_STYLES:
            self.voice_style = style_id
            return True
        return False

    def set_speed(self, speed):
        """Set speech speed."""
        if 0.5 <= speed <= 2.0:
            self.speed = speed
            return True
        return False

    def set_microphone(self, mic_name):
        """Set the microphone input device."""
        self.microphone = mic_name

    async def start_wake_word(self):
        """Start optional wake-word listening (Hey Solaris)."""
        # Wake word is optional - not mandatory
        config.VOICE_STATE = "listening"

    async def stop_wake_word(self):
        """Stop wake-word listening."""
        config.VOICE_STATE = "idle"

    async def cleanup(self):
        """Properly clean up audio resources."""
        await self.stop_listening()
        await self.stop_wake_word()
        self.is_speaking = False
        config.VOICE_STATE = "idle"
        # In a real implementation, would release sound card resources