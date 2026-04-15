from arduino.app_utils import *
import sys
 
import glob
import os

import subprocess

# Checking to see if the app was run from the App Lab and thus is in a docker
IN_DOCKER = os.path.exists("/.dockerenv")
if not IN_DOCKER:
    # Checking for the lock file if it isnt in a docker
    print("Running from OS")
    LOCK_FILE = "/tmp/penplotter_initialized"
    files = glob.glob("/home/arduino/ArduinoApps/penplotter/*.gcode")
else:
    print("Running from App-Lab")
    files = glob.glob("/app/*.gcode")

# Finding the most recently modifiyed file
GCODE_FILE = max(files, key=os.path.getmtime)  

def send_gcode_file(filepath):
    """Read a G-code file and send each line to the microcontroller, waiting for 'ok'."""
    with open(filepath, "r") as f:
        for line in f:
            # Strip whitespace
            line = line.strip()
            print(line)
            # Skip blank lines and comments
            if not line or line.startswith(";"):
                continue
 
            # Strip inline comments
            if ";" in line:
                line = line[:line.index(";")].strip()
 
            if not line:
                continue
 
            # Send line and wait for acknowledgment
            response = Bridge.call("parseGcode", line)
            if response != "ok":
                print(f"Unexpected response for '{line}': {response}")
                sys.exit(1)

print("Plot Started")
send_gcode_file(GCODE_FILE)
print("Plot Completed")