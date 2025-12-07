import matplotlib.pyplot as plt
import time
import laptop_subscriber
import queue
import threading

plt.ion()
fig, ax = plt.subplots()

time_values = []
filtered_values = []

def plot_data(data_queue):
    while True:

        filtered, state = data_queue.get()

        current_time = time.time()
        time_values.append(current_time)
        filtered_values.append(filtered)

        ax.clear()

        ax.plot(time_values, filtered_values, label="Filtered Data", color='blue')

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Filtered Value")
        ax.set_title("Real-time Sensor Data")

        ax.text(0.05, 0.95, f"State: {state}", transform=ax.transAxes, fontsize=12, verticalalignment='top', color='red')

        plt.draw()
        plt.pause(0.1)


if __name__ == "__main__":
    print("Starting the visualizer...")
    data_queue = queue.Queue()  # Create the queue for communication

    # Start the MQTT subscriber thread
    threading.Thread(target=laptop_subscriber.main, args=(data_queue,), daemon=True).start()

    # Start plotting data from the queue
    plot_data(data_queue)  # Start plotting continuously
