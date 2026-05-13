import subprocess
import sys
import os
import time
import argparse

# Argument Parse stuff
parser = argparse.ArgumentParser(prog = "plot")
verbose_arg = "v"
write_in_order_arg = "w"
parser.add_argument("file", help="File to plot")
parser.add_argument(f"-{verbose_arg}","--verbose", action="store_true", help="Print all streamed lines of GCode")
parser.add_argument(f"-{write_in_order_arg}","--write-in-order", action = "store_true",help="Writes all lines first then does text (slower)")
args = parser.parse_args()

FILE = args.file
VERBOSE = args.verbose
WRITE = args.write_in_order

def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Failed: {cmd}")
        sys.exit(1)

pdf = FILE
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
svg = os.path.join(BASE, "current.svg")
gcode = os.path.join(BASE, "current.gcode")
CONFIG = os.path.join(BASE, "svg-slicer", "config.yaml")

print("[INFO] Starting PDF to GCode slicing")
start = time.time()

run(f"PYTHONPATH=/home/arduino/ArduinoApps/penplotter/svg-slicer python3 -m svg_slicer.cli {pdf} \
    --config {CONFIG} \
    --scale auto \
    --printer-profile madsen_pen_plotter \
    --rotate 180 \
    {"--write-in-order" if WRITE else ''} \
    --output {gcode}")
elapsed = time.time() - start
print(f"[INFO] PDF to GCode took {elapsed:.2f}s")
 
ARGS = ""
if VERBOSE:
    ARGS += verbose_arg

run(f"python3 python/send_gcode.py current.gcode {'-'+ ARGS if ARGS else ''}")