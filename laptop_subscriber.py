import paho.mqtt.client as mqtt
import time
from fft_processing import add_sample
from spotify_control import play_pause_toggle, volume_control
import threading
import queue

# Configuration parameters for signals
TAP_THRESHOLD_DELTA = 150
REFRACTORY = 0.35       
COOLDOWN = 3.0    

last_clap_time = 0.0
prev_filtered = 0.0
noise_floor = 100.0
NOISE_ALPHA = 0.1

# Global state variables
raw_val = 0
filtered = 0
energy = 0
state = "Paused"
cooldown_until = 0.0
previous_volume= 0
cnt =0

def on_message(client, userdata, msg):

    data_queue = userdata 
    global last_clap_time, raw_val, filtered, prev_filtered,filtered, volume, previous_volume,cnt
    global state, noise_floor, energy, cooldown_until, energy_val

    #Pulling sensor data from MQTT
    sensor1, sensor2 = map(int, msg.payload.decode().split(","))
    payload = sensor1  
    volume = sensor2
    try:
        raw_val = int(payload)
    except:
        print("Invalid payload:", payload)
        return
    #lil bit of filtering for volume
    filtered = raw_val
    add_sample(filtered)
    volume = int((volume/1023)*100)


    #tap detection logic
    now = time.time()
    if now < cooldown_until:
        prev_filtered = filtered
        return

    #noise floor and floor shifting 
    if filtered < noise_floor + 100:
        noise_floor = (1 - NOISE_ALPHA) * noise_floor + NOISE_ALPHA * filtered

    threshold = noise_floor + TAP_THRESHOLD_DELTA

    is_rising = prev_filtered <= threshold and filtered > threshold

    #if the tap is "real" and there isn't a cooldown
    if is_rising and (now - last_clap_time) > REFRACTORY:

        #play and pause
        print("Filtered:", filtered, "Noise Floor:", noise_floor)
        if state == "Paused":
            print("Resuming Playback")
            state = "Playing"
        else:
            print("Pausing Playback")
            state = "Paused"

        play_pause_toggle()

        # timing for retrigger
        cooldown_until = now + COOLDOWN
        last_clap_time = now

    prev_filtered = filtered
    #data to vizualizer
    data_queue.put((filtered, state, volume))

    if volume-2 > previous_volume or volume+2 < previous_volume:
        print("Volume Set to: ", volume)
        volume_control(volume)
        previous_volume = volume




def start_mqtt(data_queue):
    client = mqtt.Client()
    client.user_data_set(data_queue) 
    client.on_message = on_message
    client.connect("172.20.10.7", 1883, 60)
    client.subscribe("project/raw_sound")
    print("Connected to MQTT broker.")
    client.loop_start()

def main(data_queue):
    start_mqtt(data_queue)
    print("Spotify Control Ready.")



if __name__ == "__main__":
    data_queue = queue.Queue()
    threading.Thread(target=main, args=(data_queue,), daemon=True).start()
    while True:
        time.sleep(1)