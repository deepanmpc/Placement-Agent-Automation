import os
import asyncio
import pygame

class AudioService:
    def __init__(self):
        # Initialize pygame mixer for async-friendly non-blocking playback
        pygame.mixer.init()

    async def play_audio_async(self, filepath: str):
        """Plays audio without blocking the main event loop."""
        if not os.path.exists(filepath):
            return
            
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
            
    def stop_audio(self):
        """Immediately stops any playing audio."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
