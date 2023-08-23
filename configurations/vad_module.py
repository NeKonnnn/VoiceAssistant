# vad_module.py
import webrtcvad
import numpy as np

class VADProcessor:
    def __init__(self, sample_rate=16000, frame_duration_ms=30, mode=1):
        self.vad = webrtcvad.Vad(mode)
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.num_samples_per_frame = sample_rate * frame_duration_ms // 1000
        self.buffer = np.array([], dtype=np.int16)

    def process_frame(self, frame):
        self.buffer = np.concatenate((self.buffer, frame))
        while len(self.buffer) >= self.num_samples_per_frame:
            frame_to_process = self.buffer[:self.num_samples_per_frame]
            self.buffer = self.buffer[self.num_samples_per_frame:]
            if self.vad.is_speech(frame_to_process.tobytes(), self.sample_rate):
                return True
        return False