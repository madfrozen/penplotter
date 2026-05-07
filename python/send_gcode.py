from arduino.app_utils import *
import sys
 
import os

import time
import argparse


# Argument Parse stuff
parser = argparse.ArgumentParser()
parser.add_argument("file", help="GCode file to send")
parser.add_argument("-v","--verbose", action="store_true", help="Print all streamed lines of GCode")
args = parser.parse_args()

# Finding the most recently modifiyed file
GCODE_FILE = args.file
VERBOSE = args.verbose

# Time stuff for reporting percent complete
update_time = 3.0
total_lines = sum(1 for line in open(GCODE_FILE) if line.strip() and not line.startswith(";"))

def send_gcode_file(filepath):
    # Read a G-code file and send each line to the microcontroller, waiting for 'ok'.
    total_lines = sum(1 for line in open(GCODE_FILE) if line.strip() and not line.startswith(";"))
    print(f"[INFO] Total GODE lines: {total_lines}")
    completed = 0
    last_time = time.time()
    with open(filepath, "r") as f:
        for line in f:
            # Strip whitespace
            line = line.strip()
            # Skip blank lines and comments
            if not line or line.startswith(";"):
                continue
 
            # Strip inline comments
            if ";" in line:
                line = line[:line.index(";")].strip()
 
            if not line:
                continue
 
            # Send line and wait for acknowledgment
            if VERBOSE:
                print(line)
            response = Bridge.call("parseGcode", line)
            if response != "ok":
                print(f"Unexpected response for '{line}': {response}")
                sys.exit(1)
            completed += 1
            if time.time() - last_time >= update_time:
                print(f"[INFO] Progress: {completed/total_lines*100:.1f}%")
                last_time = time.time()

print("Plot Started")
try:
    send_gcode_file(GCODE_FILE)
    print("Plot Completed")
except KeyboardInterrupt:
    print("\nCancelled - returning to home")
    Bridge.call("parseGcode", "M05")
    Bridge.call("parseGcode", "G0 X0 Y0")
    Bridge.call("parseGcode", "M03")