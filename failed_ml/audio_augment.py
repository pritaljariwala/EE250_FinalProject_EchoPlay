# audio_augment.py
import os
import librosa
import soundfile as sf
import numpy as np

# -------------------------------
# Parameters
# -------------------------------
DATA_DIR = "/Users/pritaljariwala/EE250_Fall25/EE250_FinalProject/audio_samples"      # Original audio: one file per command
AUG_DIR = "audio_augmented"     # Where augmented files will be saved
COMMANDS = ["play", "pause", "skip"]
NUM_AUG = 20                    # Number of augmented samples per original
SAMPLE_RATE = 16000

# Make output folder
os.makedirs(AUG_DIR, exist_ok=True)
for cmd in COMMANDS:
    os.makedirs(os.path.join(AUG_DIR, cmd), exist_ok=True)

# -------------------------------
# Augmentation Functions
# -------------------------------
def add_noise(y, noise_level=0.005):
    noise = np.random.randn(len(y))
    return y + noise_level * noise

def change_pitch(y, sr, n_steps):
    return librosa.effects.pitch_shift(y=y, sr=sr, n_steps=n_steps)

def change_speed(y, speed_factor):
    return librosa.effects.time_stretch(y, speed_factor)

# -------------------------------
# Generate Augmented Data
# -------------------------------
for cmd in COMMANDS:
    original_file = os.path.join(DATA_DIR, f"{cmd}.wav")  # or .mp3
    y, sr = librosa.load(original_file, sr=SAMPLE_RATE)
    
    for i in range(NUM_AUG):
        y_aug = y.copy()
        
        # Randomly apply augmentations
        if np.random.rand() < 0.5:
            y_aug = add_noise(y_aug, noise_level=np.random.uniform(0.003,0.01))
        if np.random.rand() < 0.5:
            y_aug = change_pitch(y_aug, sr, n_steps=np.random.uniform(-2,2))
        if np.random.rand() < 0.5:
            speed_factor = np.random.uniform(0.9,1.1)
            y_aug = change_speed(y_aug, speed_factor)
            # Stretching can change length, truncate or pad
            if len(y_aug) < SAMPLE_RATE:
                y_aug = np.pad(y_aug, (0, SAMPLE_RATE-len(y_aug)))
            else:
                y_aug = y_aug[:SAMPLE_RATE]
        
        out_file = os.path.join(AUG_DIR, cmd, f"{cmd}_aug_{i+1}.wav")
        sf.write(out_file, y_aug, SAMPLE_RATE)

print("Augmented dataset generated!")
