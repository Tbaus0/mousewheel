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
import numpy as np

TIMEOUT = 0.1   #global timeout

ser = serial.Serial('COM3', baudrate = 9600, timeout=TIMEOUT) #begin serial monitor analysis

#%% functions

def toggle_pause():
    global paused
    paused = not paused
    print("Paused" if paused else "Resumed")
    
def Get_numbers(data):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", data)
    
    return numbers
    
def Graph_data(wheelData):
    position = [row[0] for row in wheelData]
    position = [float(p) for p in position]
    velocity = [row[1] for row in wheelData]
    velocity = [float(v) for v in velocity]
    time = [row[2] for row in wheelData]
    time = [float(t) for t in time]

    
    x = np.arange(0,max(time),max(time)/len(time))
    #plt.subplot2grid(2,1)
    plt.figure(1)
    plt.plot(x, position, label='position')
    plt.title("Position vs time")
    plt.legend()
     
    plt.figure(2)
    plt.plot(x, velocity, label='position')
    plt.title("Velocity vs time")
    plt.legend()
    
    plt.show()

#%% working code
wheelData = []
paused = True

keyboard.on_press_key("space", lambda _: toggle_pause())    #when the space key is pressed, toggle pause variable boolean

while True:
    # Check for long spacebar hold to exit
    if keyboard.is_pressed("space"):
        start_time = time.time()
        while keyboard.is_pressed("space"):
            if time.time() - start_time >= 0.5:  # spacebar held > 0.5 seconds
                print("Spacebar held long — exiting program.")
                ser.close()                 
                Graph_data(wheelData)
                exit()
            time.sleep(TIMEOUT)

    if paused:
        time.sleep(TIMEOUT)
        continue

    if ser.in_waiting:
        data = ser.readline().decode(errors='ignore').strip()
        try:
            timestamp = time.time()-start_time
            print(data + f'  Timestamp: {timestamp:.3f}')
            wheelData.append(Get_numbers(data + f'  Timestamp: {timestamp:.3f}'))
        except ValueError:
            print("Ignored invalid data")

    time.sleep(0.05)
