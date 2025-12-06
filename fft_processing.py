# fft_processing.py

import numpy as np

FFT_SIZE = 256
sample_buffer = []

def add_sample(value: float):
    """
    Add a new filtered value to the FFT buffer (sliding window).
    """
    sample_buffer.append(value)
    if len(sample_buffer) > FFT_SIZE:
        sample_buffer.pop(0)

def compute_fft():
    """
    Compute FFT magnitude when buffer is full.
    Returns None if not enough samples yet.
    """
    if len(sample_buffer) < FFT_SIZE:
        return None

    data = np.array(sample_buffer)
    data = data - np.mean(data)  # remove DC offset

    fft_vals = np.fft.rfft(data)
    magnitudes = np.abs(fft_vals)
    return magnitudes
