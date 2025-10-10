# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 15:31:20 2025

@author: tobau
"""

import keyboard
import time
import serial
import re
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import sys

TIMEOUT = 0.1
ser = serial.Serial('COM5', baudrate=9600, timeout=TIMEOUT)

#%% functions

def Get_numbers(data):
    """Extract numeric values from a string using regex."""
    return re.findall(r"[-+]?\d*\.\d+|\d+", data)

def Graph_data(records):
    """Plot position and velocity vs time from collected records."""
    times = [r[0] for r in records]
    position = [float(r[1][0]) if len(r[1]) >= 1 else 0 for r in records]
    velocity = [float(r[1][1]) if len(r[1]) >= 2 else 0 for r in records]

    # First subplot: Position vs Time
    plt.subplot(2, 1, 1)
    plt.plot(times, position, label='position')
    plt.title("Position vs time")
    plt.xlabel('Time')
    plt.ylabel('Position (cm)')
    plt.legend()

    # Second subplot: Velocity vs Time
    plt.subplot(2, 1, 2)
    plt.plot(times, velocity, label='velocity')
    plt.title("Velocity vs time")
    plt.xlabel('Time')
    plt.ylabel('Velocity (cm/s)')
    plt.legend()

    plt.gca().set_xticklabels([])   # clears labels but leaves ticks

    plt.tight_layout()
    safe_time = times[0].replace(':', '-').replace('.', '_')
    plt.savefig(f'Wheel_data_Graphs_{safe_time}.png')

    Combine_data(records)
    plt.show()

def End_collection():
    """Stop collection, plot and save data, close serial."""
    global collection_active
    collection_active = False
    Graph_data(records)

    if ser.is_open:
        ser.close()
        sys.exit()
        print("Serial collection stopped and port closed.")
    else:
        print("Serial port was already closed.")

def Combine_data(records):
    """Save combined data (time, position, velocity) to CSV."""
    combined_data = []
    for timestamp, row in records:
        if len(row) >= 2:
            position = float(row[0])
            velocity = float(row[1])
            combined_data.append([timestamp, position, velocity])
        else:
            print(f"Skipping malformed row: {row}")

    safe_time = records[0][0].replace(':', '-').replace('.', '_')
    file_name = f'mouse-wheel-data-{safe_time}.csv'
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Position (cm)', 'Velocity (cm/s)'])
        writer.writerows(combined_data)

    print(f"Data successfully exported to {file_name}.")

#%% working code
collection_active = True
records = []  # list of (timestamp, [numbers])

# Spacebar interrupt
keyboard.on_press_key("space", lambda _: End_collection())

try:
    while collection_active:
        data = ser.readline().decode(errors='ignore').strip()
        numbers = Get_numbers(data)
        if numbers:  # only append if valid numbers found
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(data + f'  Timestamp: {timestamp}')
            records.append((timestamp, numbers))
        time.sleep(TIMEOUT)
finally:
    if ser.is_open:
        ser.close()
    else:
        print("Serial port was already closed.") 
