import paho.mqtt.client as mqtt
import time
from filters import moving_average
from fft_processing import add_sample, compute_fft 

# Thresholds for clap detection
TAP_THRESHOLD = 600
DOUBLE_TAP_WINDOW = 1  # seconds
last_clap_time = 0

def on_message(client, userdata, msg):
    raw_value = int(msg.payload.decode())
    print("Received:", raw_value)

    try:
        raw_val = int(msg.payload.decode())

        # 1. Filter
        filtered = moving_average(raw_val)

        # 2. Add to FFT buffer
        add_sample(filtered)

        # 3. Compute FFT when ready
        fft_mag = compute_fft()
        if fft_mag is not None:
            energy = fft_mag.sum()
            print(f"Raw={raw_val}, Filtered={filtered:.2f}, FFT Energy={energy:.2f}")
        else:
            print(f"Raw={raw_val}, Filtered={filtered:.2f}")


        # Clap detection logic
        now = time.time()
        if filtered > TAP_THRESHOLD and (now - last_clap_time) > 0.2:
            # Check for double clap
            if (now - last_clap_time) < DOUBLE_TAP_WINDOW:
                print("DOUBLE TAP → skip track")
                # <-- your Spotify skip function
            else:
                print("SINGLE TAP → toggle play/pause")
                # <-- your Spotify toggle function
            last_clap_time = now

    except ValueError:
        print("Invalid payload received.")

client = mqtt.Client()
client.on_message = on_message

client.connect("172.20.10.6", 1883, 60)
client.subscribe("project/raw_sound")

client.loop_forever()
