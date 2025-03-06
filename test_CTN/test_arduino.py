import serial
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import time
import numpy as np

# Configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Replace with your serial port
BAUD_RATE = 115200              # Match this to your Arduino's baud rate
CSV_FILE = 'arduino_data.csv' # Output CSV file

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
input("Press enter to start...")
print("Starting in 2s...")
time.sleep(2)
print("Starting now !")
# Function to update the plot
start = time.perf_counter()

data = []
while True:
    try:
        if ser.in_waiting > 0:
            line_data = ser.readline().decode('utf-8').strip()
            D = line_data.split(", ")
            data.append( [float(D[0]), float(D[1])] )
            # print(f"Received: {line_data}")
        else:
            time.sleep(0.01)  # Small sleep to avoid busy-waiting
    except Exception as e:
        pass
        # print(f"Error: {e}")
    if time.perf_counter() - start > 8:
        break
ser.close()

data = np.array(data)
np.savetxt("arduino_xy.csv", data)
print(data)
