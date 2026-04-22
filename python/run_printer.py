import subprocess
import sys
import os
import time

def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Failed: {cmd}")
        sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 plot.py <file.pdf>")
    sys.exit(1)

pdf = sys.argv[1]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
svg = os.path.join(BASE, "current.svg")
gcode = os.path.join(BASE, "current.gcode")

run(f"python3 python/slice_pdf.py {pdf}")
start = time.time()
run(f"PYTHONPATH=/home/arduino/ArduinoApps/penplotter/svg-slicer python3 -m svg_slicer.cli {svg} \
    --config svg-slicer/config.yaml \
    --scale auto \
    --printer-profile madsen_pen_plotter \
    --output {gcode}")
elapsed = time.time() - start
print(f"[INFO] SVG to GCode took {elapsed:.2f}s")
run(f"python3 python/send_gcode.py")