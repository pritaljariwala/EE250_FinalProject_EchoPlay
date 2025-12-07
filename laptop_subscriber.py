#windows laptop_subscriber.py
import paho.mqtt.client as mqtt
import time
import socket
import threading
from filters import moving_average
from fft_processing import add_sample, compute_fft 
from spotify_control import play_pause_toggle, skip_track

# Thresholds for clap detection
TAP_THRESHOLD = 700
DOUBLE_TAP_WINDOW = 1  # seconds

TCP_HOST = "172.20.10.7"  # Bind to all available network interfaces
TCP_PORT = 65432   

data_lock = threading.Lock()

last_clap_time = 0.0
prev_filtered = 0.0
state = "Paused"

def handle_client_connection(conn):
    try:
        while True:
            with data_lock:
            # Send the latest data to the front-end (UI)
                data = f"Raw: {raw_val}, Filtered: {filtered}, Playback: {state}"
                conn.sendall(data.encode('utf-8'))
            time.sleep(1)
    except Exception as e:
        print(f"TCP Error: {e}")
    finally:
        conn.close()

def start_tcp_server():
    # Create the TCP socket and bind it to the host and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(1)
        print(f"TCP Server listening on {TCP_HOST}:{TCP_PORT}")

        while True:
            # Accept incoming TCP connection
            conn, addr = server_socket.accept()
            print(f"Connection established with {addr}")

            # Handle the connection in a separate thread
            threading.Thread(target=handle_client_connection, args=(conn,)).start()

def on_message(client, userdata, msg):
    global last_clap_time, filtered, raw_val

    try:
        raw_val = int(msg.payload.decode())
    except ValueError:
        print("Invalid payload received:", msg.payload)
        return

    # Basic logging
    print("Received:", raw_val)

    # 1. Filter
    #filtered = moving_average(raw_val)
    filtered = raw_val
    # 2. Add to FFT buffer
    add_sample(raw_val)

    # 3. Compute FFT
    fft_mag = compute_fft()
    if fft_mag is not None:
        energy = fft_mag.sum()
        print(f"Raw={raw_val}, Filtered={filtered:.2f}, FFT Energy={energy:.2f}")
    else:
        print(f"Raw={raw_val}, Filtered={filtered:.2f}")

    # 4. Clap detection
    is_rising = prev_filtered <= TAP_THRESHOLD and filtered > TAP_THRESHOLD

    now = time.time()

    if is_rising and (now - last_clap_time) > 0.2:
        dt = now - last_clap_time
        if 0 < (now - last_clap_time) < DOUBLE_TAP_WINDOW:
            state = "Skipped"
            print("DOUBLE TAP → skip track")
            skip_track()
        else:
            print("SINGLE TAP → toggle play/pause")
            if state == "Paused":
                state = "Playing"
            elif state == "Playing":
                state = "Paused"
            play_pause_toggle()

        last_clap_time = now
    
    prev_filtered = filtered

def start_mqtt():
    # Initialize the MQTT client
    client = mqtt.Client()
    client.on_message = on_message

    try:
        # Connect to the MQTT broker
        client.connect("172.20.10.7", 1883, 60)
        print("Connected to MQTT broker.")
        
        # Subscribe to the relevant topic
        client.subscribe("project/raw_sound")

        # Start the MQTT loop in the background
        client.loop_start()  # Non-blocking
    except Exception as e:
        print(f"Error starting MQTT client: {e}")


if __name__ == "__main__":
    # Start MQTT client in a separate thread
    threading.Thread(target=start_mqtt, daemon=True).start()

    # Start the TCP server in the main thread
    start_tcp_server()