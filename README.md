# 🖊️ PenPlotter
### Todo
- Add CLI for moving with gcode from terminal

## Getting The Code
Connect you you Arduino Uno Q and open a terminal in it.  
`cd` into the `ArduinoApps` directory and clone this repo
```bash
cd ~/ArduinoApps/
git clone put url here
```
### Installing Dependencies
Clone the Arduino-app-utils repo and install it with pip3  
You might need to `sudo apt install pip3`
```bash
cd ~
git clone https://github.com/arduino/app-bricks-py.git ~/arduino-app-utils
cd ~/arduino-app-utils
sudo pip3 install . --break-system-packages
```
Add it to your path
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
You will also need to add `numpy` and `watchdog`.
```bash
sudo pip3 install numpy watchdog --break-system-packages
```
I know these the first two exist somewhere on the board but I haven't been able to find them yet, so for now we get an extra copy.

## Clone acmattons pdf/svg to gcode slicer
First cd into the new `penplotter` directory and clone the repo there
```bash
cd penplotter/
git clone https://github.com/acmattson3/svg-slicer
```
Then install the dependencies
```bash
sudo apt-get install python3-svgelements shapely PyYAML matplotlib Pillow PyMuPDF Hershey-Fonts
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
You will need to put the pdf file that you want to plot on to the board.
```bash
#example: run this on your computer, not the Arduino
scp path_to_file/file.pdf arduino@[boardname].local:~/ArduinoApps/penplotter
```
This will put your file into the proper directory on your Uno Q.