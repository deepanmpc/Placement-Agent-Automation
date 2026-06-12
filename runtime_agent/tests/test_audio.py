import pytest
import os
import wave
import numpy as np
from runtime_agent.services.tts_service import TTSService

def test_tts_generation():
    tts = TTSService()
    
    # Generate a short TTS clip
    audio_path = tts.generate_audio("Testing 1 2 3.")
    
    assert audio_path != ""
    assert os.path.exists(audio_path)
    
    # Verify it is a valid audio file (either AIFF from say, or WAV from piper)
    assert os.path.getsize(audio_path) > 1000
    
    # Cleanup
    os.remove(audio_path)
    
def test_dummy_audio_creation(tmp_path):
    # This verifies the soundfile/numpy dependencies are correctly installed
    import soundfile as sf
    test_file = tmp_path / "test.wav"
    dummy_data = np.zeros(16000, dtype=np.float32) # 1 sec of silence
    sf.write(test_file, dummy_data, 16000)
    
    assert os.path.exists(test_file)
