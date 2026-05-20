import sounddevice as sd
import soundfile as sf
import queue
import numpy as np
import os
from datetime import datetime
from runtime_agent.config import Config

class MicrophoneService:
    def __init__(self):
        self.output_dir = os.path.join(Config.OUTPUT_DIR, "audio")
        self.sample_rate = 16000
        self.channels = 1

    def record_until_keypress(self) -> str:
        q = queue.Queue()
        
        def callback(indata, frames, time, status):
            if status:
                print(status, flush=True)
            q.put(indata.copy())
            
        print("\n[bold yellow]🎙️  Press ENTER to start recording...[/bold yellow]")
        input()
        print("[bold red]🔴 Recording... (Press ENTER to stop)[/bold red]")
        
        stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback)
        with stream:
            input()
            
        print("[dim]⏹️ Stopped recording.[/dim]")
        
        data = []
        while not q.empty():
            data.append(q.get())
            
        if not data:
            return ""
            
        audio_data = np.concatenate(data, axis=0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, f"recording_{timestamp}.wav")
        
        sf.write(filepath, audio_data, self.sample_rate)
        return filepath
