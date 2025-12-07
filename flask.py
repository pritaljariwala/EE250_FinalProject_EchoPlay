import socket
import threading
from flask import Flask, render_template
import time

# Flask app setup
app = Flask(__name__)

# Variables to store incoming data
raw_data = "Waiting for raw data..."
processed_data = "Waiting for processed data..."
playback_state = "Paused"

# TCP server setup
TCP_HOST = "172.20.10.7"   # Listen on all available interfaces
TCP_PORT = 65432        # Port to listen for incoming data

def handle_client_connection(conn):
    global raw_data, processed_data, playback_state

    try:
        while True:
            # Receive data from the client (Laptop 1)
            data = conn.recv(1024)
            if not data:
                break
            # Decode the data (you can send raw data, filtered data, or other info)
            raw_data = data.decode('utf-8')
            processed_data = f"Processed: {raw_data}"

            # Here, you can add more logic to process the received data (FFT, playback, etc.)
            # Example: Simulating playback state toggle based on received data
            if "clap" in raw_data:
                playback_state = "Play" if playback_state == "Paused" else "Paused"

            print(f"Received data: {raw_data}")
            
            # Simulate some response back to the sender if needed (e.g., acknowledge receipt)
            conn.sendall(b"Data received and processed")

    finally:
        conn.close()

def start_tcp_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TCP_HOST, TCP_PORT))
    server_socket.listen(1)
    print("Server listening on port", TCP_PORT)

    while True:
        # Accept incoming connections
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        # Handle the client connection in a separate thread
        threading.Thread(target=handle_client_connection, args=(conn,)).start()

@app.route('/')
def index():
    return render_template('index.html', 
                           raw_data=raw_data, 
                           processed_data=processed_data,
                           playback_state=playback_state)

if __name__ == "__main__":
    # Start the TCP server in a separate thread
    threading.Thread(target=start_tcp_server, daemon=True).start()
    # Run the Flask app (web interface)
    app.run(host="0.0.0.0", port=5000)  # Run Flask app
