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

TIMEOUT = 0.1   #global timeout

ser = serial.Serial('COM3', baudrate = 9600, timeout=TIMEOUT)
wheelData = []

#%% functions

def toggle_pause():
    global paused
    paused = not paused
    print("Paused" if paused else "Resumed")
    
def Get_numbers(string):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", string)
    
    return numbers
    
#def Graph():
    



#%% working code
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
                #Graph(wheelData)
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
