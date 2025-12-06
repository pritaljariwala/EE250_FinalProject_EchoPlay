#!/usr/bin/env python3
import time
import numpy as np
from grovepi import analogRead
import paho.mqtt.client as mqtt


# -----------------------------------------------------------
# Configuration Parameters
# -----------------------------------------------------------

SOUND_SENSOR_PORT = 0             # A0 on GrovePi
SAMPLE_INTERVAL = 0.01            # 10 ms sampling
WINDOW_SIZE = 5                   # Filter window length
FFT_WINDOW_SIZE = 256             # Number of samples for FFT (optional)
CLAP_THRESHOLD = 300              # Adjust after calibration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "echoplay/sound"


# -----------------------------------------------------------
# MQTT Setup
# -----------------------------------------------------------

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()


# Moving Average Filter

filter_buffer = []

def moving_average(new_value: float) -> float:
    filter_buffer.append(new_value)
    if len(filter_buffer) > WINDOW_SIZE:
        filter_buffer.pop(0)
    return sum(filter_buffer) / len(filter_buffer)


# FFT Computation 

def compute_fft(window):
    fft_vals = np.fft.rfft(window)
    fft_mag = np.abs(fft_vals)
    return fft_mag.max()


# -----------------------------------------------------------
# Main Processing Loop
# -----------------------------------------------------------

def run_signal_processor():
    print("[SignalProcessor] Starting continuous sampling...")

    fft_window = []

    try:
        while True:
            raw = analogRead(SOUND_SENSOR_PORT)
            filtered = moving_average(raw)

            # Build FFT window
            fft_window.append(filtered)
            if len(fft_window) > FFT_WINDOW_SIZE:
                fft_window.pop(0)

            # Optional FFT peak magnitude
            if len(fft_window) == FFT_WINDOW_SIZE:
                fft_peak = compute_fft(fft_window)
            else:
                fft_peak = 0

            # Publish only when amplitude exceeds threshold
            if filtered > CLAP_THRESHOLD:
                payload = {
                    "raw": int(raw),
                    "filtered": float(filtered),
                    "fft_peak": float(fft_peak),
                    "timestamp": time.time()
                }
                client.publish(MQTT_TOPIC, str(payload))
                print("[SignalProcessor] Event published:", payload)

                # Simple debounce to avoid false double triggers
                time.sleep(0.15)

            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("\n[SignalProcessor] Stopped.")
    finally:
        client.loop_stop()


# -----------------------------------------------------------
# Entry Point
# -----------------------------------------------------------

if __name__ == "__main__":
    run_signal_processor()
