# -*- coding: utf-8 -*-
"""
Serial Reading Script for Arduino

Takes in serial data from the serial monitor and outputs data with
associated graphs

"""
import keyboard
import time
import serial
import re     #regular expressions (regex)
import matplotlib.pyplot as plt

from datetime import datetime
import csv
import sys



TIMEOUT = 0.1   #global timeout

ser = serial.Serial('COM3', baudrate = 9600, timeout=TIMEOUT) #begin serial monitor analysis

#%% functions

    
def Get_numbers(data):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", data)
    
    return numbers
    
def Graph_data(wheelData,times):
    position = []
    for row in wheelData:
        if len(row) >= 2:
            position.append(float(row[0]))
        else:
            position.append(0)
    
    velocity = []
    for row in wheelData:
        if len(row) >= 2:
            velocity.append(float(row[1]))
        else:
            velocity.append(0)
     
    

    
    #x = np.arange(0,max(position),max(position)/len(position))
    plt.subplot(1, 2, 1)
    
    plt.plot(times, position, label='position')
    plt.title("Position vs time")
    plt.xlabel('Time')
    plt.ylabel('Position (cm/s)')

    plt.legend()
   

    
    #x = np.arange(0,max(velocity),max(velocity)/len(velocity))
    plt.subplot(1, 2, 2)

    plt.plot(times, velocity, label='position')
    plt.title("Velocity vs time")
    plt.xlabel('Time')
    plt.ylabel('Velocity (cm/s)')

    plt.legend()
   
    safe_time = times[0].replace(':', '-').replace('.', '_')
    plt.savefig(f'Wheel_data_Graphs_{safe_time}')
    
    Combine_data(wheelData, times)
    plt.show()

def End_collection():
    global collection_active
    collection_active = False  # signal to stop collecting
    Graph_data(wheelData, times)

    if ser.is_open:
        ser.close()
        sys.exit()
        print("Serial collection stopped and port closed.")
    else:
        print("Serial port was already closed.")
        
def Combine_data(wheelData, times):
    combined_data = []

# Build rows: [time, position, velocity]
    for row, timestamp in zip(wheelData, times):
        if len(row) >= 2:  # ensure position and velocity exist
            position = float(row[0])
            velocity = float(row[1])
            combined_data.append([timestamp, position, velocity])
        else:
            print(f"Skipping malformed row: {row}")

    safe_time = times[0].replace(':', '-').replace('.', '_')
    file_name = f'mouse-wheel-data-{safe_time}'
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file,)
        writer.writerow(['Time', 'Position (cm)', 'Velocity (cm/s)'])  # header
        writer.writerows(combined_data)

    print("Data successfully exported to wheel_output.csv.")


#%% working code
collection_active = True       #for end_collection function
wheelData = []
times = []

# Set up the spacebar interrupt
keyboard.on_press_key("space", lambda _: End_collection())
  
# data = ser.readline().decode(errors='ignore').strip()
# while data != 'Position (cm): 0.00	 Velocity (cm/s): 0.00	 Direction: Stopped':
#     time.sleep(0.5)
# else:
#     pass

# Main loop
try:
    while collection_active:
        data = ser.readline().decode(errors='ignore').strip()
        try:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # HH:MM:SS.sss
            print(data + f'  Timestamp: {timestamp}')
            wheelData.append(Get_numbers(data))
            times.append(timestamp)
        except ValueError:
                print("Ignored invalid data")
    
        time.sleep(TIMEOUT)
finally:
    if ser.is_open:
        ser.close()
    else:
        print("Serial port was already closed.")
