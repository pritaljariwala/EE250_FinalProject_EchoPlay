import matplotlib.pyplot as plt
import time
import laptop_subscriber

plt.ion()
fig, ax = plt.subplots()

time_values = []
filtered_values = []

def plot_data():
    while True:

        current_time = time.time()
        time_values.append(current_time)
        filtered_values.append(laptop_subscriber.filtered)

        ax.clear()

        ax.plot(time_values, filtered_values, label="Filtered Data", color='blue')

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Filtered Value")
        ax.set_title("Real-time Sensor Data")

        ax.text(0.05, 0.95, f"State: {laptop_subscriber.state}", transform=ax.transAxes, fontsize=12, verticalalignment='top', color='red')

        plt.draw()
        plt.pause(0.1)


if __name__ == "__main__":
    print("Starting the visualizer...")
    plot_data()  # Start plotting continuously
