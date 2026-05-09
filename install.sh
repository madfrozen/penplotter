set -e

sudo apt install python3-pip

echo "Cloning Arduino App Bricks repo and installing"
git clone https://github.com/arduino/app-bricks-py.git ~/arduino-app-utils
sudo pip3 install ~/arduino-app-utils --break-system-packages

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo "alias plot='python3 ~/ArduinoApps/penplotter/python/run_printer.py'" >> ~/.bashrc

sudo pip3 install numpy watchdog --break-system-packages

echo "Cloning Acmattson's PDF/SVG Slicer and installing dependencies"
git clone https://github.com/acmattson3/svg-slicer ~/ArduinoApps/penplotter

sudo pip3 install svgelements shapely PyYAML matplotlib Pillow PyMuPDF Hershey-Fonts --break-system-packages

echo "Adding UNO Q board to arduino-cli"
arduino-cli core install arduino:zephyr

echo "Adding required libraries: Arduino_RouterBridge, AccelStepper"
arduino-cli lib install Arduino_RouterBridge AccelStepper

bash upload.sh

echo -e "\e[33mInstall complete\e[0m"
echo -e "\e[31mPlease run 'source ~/.bashrc' to add libs to path\e[0m"