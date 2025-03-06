import serial
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import numpy as np

# Configuration
SERIAL_PORT = '/dev/ttyUSB2'  # Replace with your serial port
BAUD_RATE = 74880              # Match this to your Arduino's baud rate
CSV_FILE = 'arduino_data2.csv' # Output CSV file
MAX_POINTS = 1000              # Maximum number of points to display

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Initialize data containers - defined globally
timestamps = []
data_values = []

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
line_ext, = ax.plot_date([], [], '-', markersize=0)
line_int, = ax.plot_date([], [], '-', markersize=0)
line_batt, = ax.plot_date([], [], '-', markersize=0)
ax.set_xlabel('Time')
ax.set_ylabel('Data Value')
ax.set_title('Real-Time Arduino Data')
ax.grid(True)

# Format the x-axis to show time correctly
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
fig.autofmt_xdate()

# Function to update the plot
def update_plot(frame):
    global timestamps, data_values  # Use global variables

    try:
        # Read data from the serial port

        line_data = ser.readline();
        print(f"raw_line=`{line_data}`")
        line_data = line_data.decode('utf-8').strip()

        if line_data and line_data[0].isdigit():  # Allow negative numbers
            # Get the current timestamp
            current_time = datetime.now()
            timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

            data = line_data.split(', ')

            # Convert data to integer
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
                ax.set_xlim(
                    timestamps[0],
                    timestamps[-1] + timedelta(seconds=buffer)
                )

            # Dynamically adjust y-axis to fit the actual data values
            if data_values:
                data_min = dtv.min()
                data_max = dtv.max()
                buffer = (data_max - data_min) * 0.1 if data_max > data_min else 1000
                ax.set_ylim(data_min - buffer, data_max + buffer)

    except Exception as e:
        print(f"Error: {e}")

    # Redraw the canvas
    fig.canvas.draw()

    return line_ext,line_int, line_batt

# Set up animation
ani = animation.FuncAnimation(
    fig, 
    update_plot,
    interval=100,  # Update every 100ms
    blit=False  # Set to False to force redraw of the entire canvas
)

# Show the plot
plt.tight_layout()
plt.show()

# Close the serial connection when the plot window is closed
print("Closing serial connection...")
ser.close()
