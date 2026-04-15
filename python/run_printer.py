import subprocess
import sys
import os

def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Failed: {cmd}")
        sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 plot.py <file.pdf>")
    sys.exit(1)

pdf = sys.argv[1]
svg = pdf.replace(".pdf", ".svg")
gcode = pdf.replace(".pdf", ".gcode")

run(f"python3 slice_pdf.py {pdf}")
run(f"svg_slicer {svg} {gcode}")
run(f"python3 send_gcode.py {gcode}")