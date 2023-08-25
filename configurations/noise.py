import numpy as np

AMPLITUDE_THRESHOLD = 60  # Экспериментальное значение

def calculate_amplitude(data):
    samples = np.frombuffer(data, dtype=np.int16)
    amplitude = np.mean(np.abs(samples))
    return amplitude

def is_noise(data):
    amplitude = calculate_amplitude(data)
    print(f"Amplitude: {amplitude}")  # Debugging line
    return amplitude < AMPLITUDE_THRESHOLD