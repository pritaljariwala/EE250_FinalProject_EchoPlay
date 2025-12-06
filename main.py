import grovepi
import time
from filters import moving_average
from fft_processing import add_sample, compute_fft

# --- Sensor & playback setup ---
SOUND_SENSOR = 0
grovepi.pinMode(SOUND_SENSOR, "INPUT")

RAW_THRESHOLD = 600            # threshold for detecting a clap
DEBOUNCE_SECONDS = 0.3         # minimum time between events
last_event_time = 0
playback = "paused"            # current playback state

# Optional: FFT threshold for future frequency-based detection
FREQ_ENERGY_THRESHOLD = 20000

# --- Main loop ---
while True:
    try:
        # 1. Read raw analog value
        raw_value = grovepi.analogRead(SOUND_SENSOR)

        # 2. Apply moving average filter
        filtered_value = moving_average(raw_value)

        # 3. Add to FFT buffer
        add_sample(filtered_value)

        # 4. Compute FFT magnitude if buffer is full
        fft_magnitude = compute_fft()
        if fft_magnitude is not None:
            total_energy = fft_magnitude.sum()
            print(f"Raw={raw_value}, Filtered={filtered_value:.2f}, FFT Energy={total_energy:.2f}")
        else:
            print(f"Raw={raw_value}, Filtered={filtered_value:.2f}")

        # 5. Clap detection with debounce
        now = time.time()
        if filtered_value > RAW_THRESHOLD and (now - last_event_time) > DEBOUNCE_SECONDS:
            last_event_time = now

            # Toggle playback
            if playback == "paused":
                playback = "play"
            else:
                playback = "paused"

            print(f"CLAP DETECTED! Playback is now: {playback}")

        time.sleep(0.005)  # ~200 Hz sampling rate

    except IOError:
        print("Sensor read error")
