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
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
svg = os.path.join(BASE, "current.svg")
gcode = os.path.join(BASE, "current.gcode")

run(f"python3 slice_pdf.py {pdf}")
run(f"python3 -m svg_slicer.cli {svg} \
  --config config.yaml \
  --printer-profile madsen_pen_plotter \
  --output {gcode}")
run(f"python3 send_gcode.py")