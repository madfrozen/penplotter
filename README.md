# 🖊️ PenPlotter
### Todo
- Add CLI for moving with gcode from terminal
- Add Mcommand for vacuum bed on off

## Getting The Code
Connect you you Arduino Uno Q and open a terminal in it.  
`cd` into the `ArduinoApps` directory and clone this repo
```bash
cd ~/ArduinoApps/
git clone put url here
```
### Running the python without App Lab
Clone the Arduino-app-utils repo and install it with pip3  
You might need to `sudo apt install pip3`
```bash
cd ~
git clone https://github.com/arduino/app-bricks-py.git ~/arduino-app-utils
cd ~/arduino-app-utils
pip3 install . --break-system-packages
```
Add it to your path
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
You will also need to add `numpy`, `watchdog`, and a few others.
```bash
pip3 install numpy watchdog hershey-fonts pymupdf --break-system-packages
```
I know these the first two exist somewhere on the board but I haven't been able to find them yet, so for now we get an extra copy.

## Clone acmattons svg to gcode slicer
First cd into the new `penplotter` directory and clone the repo there
```bash
cd penplotter/
git clone https://github.com/acmattson3/svg-slicer
```
Then install the dependencies
```bash
sudo apt-get install python3-svgelements python3-shapely python3-yaml python3-matplotlib
```
We drop the needed dependencies for the GUI as it will just be running headless. Feel free to also delete the `examples` folder.
## First time start up
Before you can use the plotter for the first time you will need to compile and flash the firmware

The first step is to install the needed libraries and board into the `arduino-cli`
```bash
arduino-cli core install arduino:zephyr
arduino-cli lib install Arduino_RouterBridge AccelStepper
```
Then you can run the upload script to compile then flash to the board
```bash
bash upload.sh
```
## Using the printer
There are to ways to use the printer. The first way is by manuly putting a pdf on it by using `scp`
```bash
#example: run this on your computer, not the Arduino
scp path_to_file/file.pdf arduino@[boardname].local:~/ArduinoApps/penplotter
```
The second way is to set up a CUPS print server to be able to print your pdf from system dialog on your main computer