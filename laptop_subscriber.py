import paho.mqtt.client as mqtt
import time
from filters import moving_average
from fft_processing import add_sample, compute_fft 
from spotify_control import play_pause_toggle, skip_track

# =======================
# Detection parameters
# =======================
TAP_THRESHOLD_DELTA = 150
DOUBLE_TAP_WINDOW = 1.0
REFRACTORY = 0.35        # ignore events for 350ms
COOLDOWN = 2.0           # ignore EVERYTHING for 2 seconds after a tap

last_clap_time = 0.0
prev_filtered = 0.0
noise_floor = 100.0
NOISE_ALPHA = 0.1

raw_val = 0
filtered = 0
energy = 0
state = "Paused"
cooldown_until = 0.0

# =======================
# MQTT callback
# =======================
def on_message(client, userdata, msg):
    global last_clap_time, raw_val, filtered, prev_filtered, filtered
    global state, noise_floor, energy, cooldown_until

    payload = msg.payload.decode()

    try:
        raw_val = int(payload)
    except:
        print("Invalid payload:", payload)
        return

    print("Received:", raw_val)

    # Filtering & FFT
    add_sample(filtered)
    filtered = raw_val
    fft_mag = compute_fft()
    if fft_mag is not None:
        energy = fft_mag.sum()

    now = time.time()

    # =======================
    # COOLDOWN CHECK
    # =======================
    if now < cooldown_until:
        prev_filtered = filtered
        return

    # =======================
    # NOISE FLOOR UPDATE
    # =======================
    if filtered < noise_floor + 100:
        noise_floor = (1 - NOISE_ALPHA) * noise_floor + NOISE_ALPHA * filtered

    threshold = noise_floor + TAP_THRESHOLD_DELTA

    # =======================
    # RISING EDGE DETECTION
    # =======================
    is_rising = prev_filtered <= threshold and filtered > threshold

    if is_rising and (now - last_clap_time) > REFRACTORY:

        # SINGLE TAP
        print("Filtered:", filtered, "Noise Floor:", noise_floor)
        print("Cooldown for 2 seconds...\n")

        if state == "Paused":
            state = "Playing"
        else:
            state = "Paused"

        play_pause_toggle()

        # Apply cooldown so ringing cannot retrigger
        cooldown_until = now + COOLDOWN
        last_clap_time = now

    prev_filtered = filtered


# =======================
# MQTT STARTER
# =======================
def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("172.20.10.7", 1883, 60)
    client.subscribe("project/raw_sound")
    print("Connected to MQTT broker.")
    client.loop_start()


# =======================
# MAIN
# =======================
if __name__ == "__main__":
    start_mqtt()
    print("Spotify Control Ready.")
    while True:
        time.sleep(1)