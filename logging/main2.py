import serial
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import numpy as np

# Configuration
SERIAL_PORT = '/dev/ttyUSB1'  # Replace with your serial port
BAUD_RATE = 74880              # Match this to your Arduino's baud rate
CSV_FILE = 'arduino_data2.csv' # Output CSV file
MAX_POINTS = 1000              # Maximum number of points to display

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Initialize data containers - defined globally
timestamps = []
data_values = []

# Create figure and subplots
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.subplots_adjust(hspace=0.5, wspace=0.3)

# Initialize lines for each subplot with different colors
line_ext, = axs[0, 0].plot_date([], [], '-', markersize=0, color='r', label='Temp Ext')
line_int, = axs[0, 1].plot_date([], [], '-', markersize=0, color='g', label='Temp Int')
line_batt, = axs[1, 0].plot_date([], [], '-', markersize=0, color='b', label='Battery Voltage')

# Set titles and labels for each subplot
axs[0, 0].set_xlabel('Time')
axs[0, 0].set_ylabel('Temp Ext')
axs[0, 0].set_title('External Temperature')
axs[0, 0].grid(True)
axs[0, 0].legend()

axs[0, 1].set_xlabel('Time')
axs[0, 1].set_ylabel('Temp Int')
axs[0, 1].set_title('Internal Temperature')
axs[0, 1].grid(True)
axs[0, 1].legend()

axs[1, 0].set_xlabel('Time')
axs[1, 0].set_ylabel('Battery Voltage')
axs[1, 0].set_title('Battery Voltage')
axs[1, 0].grid(True)
axs[1, 0].legend()

# Hide the empty subplot
axs[1, 1].axis('off')

# Format the x-axis to show time correctly for all subplots
for ax in axs.flat:
    if ax != axs[1, 1]:  # Skip the empty subplot
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        # fig.autofmt_xdate()  # Rotate and align x-axis labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')

# Function to update the plot
def update_plot(frame):
    global timestamps, data_values  # Use global variables

    try:
        # Read data from the serial port
        line_data = ser.readline()
        line_data = line_data.decode('utf-8').strip()

        if line_data and line_data[0].isdigit():  # Allow negative numbers
            # Get the current timestamp
            current_time = datetime.now()
            timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

            data = line_data.split(', ')

            # Convert data to float
            tempExt = float(data[0])
            tempInt = float(data[1])
            battVolt = float(data[2])

            # Log data to CSV
            with open(CSV_FILE, mode='a', newline='') as file:
                csv_writer = csv.writer(file)
                if file.tell() == 0:  # Write header if file is empty
                    csv_writer.writerow(['timestamp', 'tempExt', 'tempInt', 'battVolt'])
                csv_writer.writerow([timestamp_str, tempExt, tempInt, battVolt])

            # Update data containers
            timestamps.append(current_time)
            data_values.append((tempExt, tempInt, battVolt))

            # Keep only the most recent data points
            if len(timestamps) > MAX_POINTS:
                timestamps = timestamps[-MAX_POINTS:]
                data_values = data_values[-MAX_POINTS:]

            dtv = np.array(data_values)
            # Update the plot data
            line_ext.set_xdata(timestamps)
            line_ext.set_ydata(dtv[:,0])
            line_int.set_xdata(timestamps)
            line_int.set_ydata(dtv[:,1])
            line_batt.set_xdata(timestamps)
            line_batt.set_ydata(dtv[:,2])

            # Adjust x-axis limits to show the time window
            if len(timestamps) > 1:
                time_range = (timestamps[-1] - timestamps[0]).total_seconds()
                buffer = max(time_range * 0.05, 1)  # 5% buffer or at least 1 second
                for ax in axs.flat:
                    if ax != axs[1, 1]:  # Skip the empty subplot
                        ax.set_xlim(
                            timestamps[0],
                            timestamps[-1] + timedelta(seconds=buffer)
                        )

            # Dynamically adjust y-axis to fit the actual data values
            if data_values:
                for ax, idx in zip([axs[0, 0], axs[0, 1], axs[1, 0]], [0, 1, 2]):
                    data_min = dtv[:, idx].min()
                    data_max = dtv[:, idx].max()
                    buffer = (data_max - data_min) * 0.1 if data_max > data_min else 0.1
                    ax.set_ylim(data_min - buffer, data_max + buffer)

    except Exception as e:
        print(f"Error: {e}")

    # Redraw the canvas
    fig.canvas.draw()

    return line_ext, line_int, line_batt

# Set up animation
ani = animation.FuncAnimation(
    fig, 
    update_plot,
    interval=100,  # Update every 100ms
    blit=False  # Set to False to force redraw of the entire canvas
)

# Show the plot
plt.tight_layout(pad=2.0)  # Increase padding to make room for rotated labels
plt.show()

# Close the serial connection when the plot window is closed
print("Closing serial connection...")
ser.close()
