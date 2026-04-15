# 🖊️ PenPlotter
### Todo
- Add unknown G code error out
- Add CLI for moving with gcode from terminal
## Running the python without App Lab
Clone the Arduino-app-utils repo and install it with pip3  
You might need to `sudo apt install pip3`
```bash
git clone https://github.com/arduino/app-bricks-py.git ~/arduino-app-utils
cd ~/arduino-app-utils
pip3 install . --break-system-packages
```
Add it to your path
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
You will also need to add `numpy`, `watchdog`, and a few others
```bash
pip3 install numpy --break-system-packages
pip3 install watchdog --break-system-packages
pip3 install hershey-fonts --break-system-packages
pip3 install pymupdf --break-system-packages
```
I know these all exist somewhere on the board but In3 haven't been able to find them yet, so for now we get an extra copy.

### Clone acmattons svg to gcode slicer
```bash
git clone https://github.com/acmattson3/svg-slicer
```
Then install the dependencies
```bash
sudo apt-get install python3-svgelements python3-shapely python3-yaml python3-matplotlib
```
we drop the needed dependencies for the GUI as it will just be running headless. Feel free to also delete the `examples` folder.
## Running the plotter without App Lab
It appears that the STM32 MC doesn't restart after the board is power cycled. To get around this the sketch needs to be re-uploaded on power cycle. This can be done with the `arduino-cli`
```bash
arduino-cli upload --fqbn arduino:zephyr:unoq --port /dev/ttyHS1 ~/ArduinoApps/penplotter/sketch
```
Alternatively you can start the app with the `arduino-app-cli` but this is undesired as the re-compiles everything and spins up a docker container for the app to run in which is a far slower process. Currently this will also reprint the most recent document in the PlotJobs directory.
```bash
arduino-app-cli app start penplotter/
```
