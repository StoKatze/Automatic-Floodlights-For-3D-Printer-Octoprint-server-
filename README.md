# Automatic Floodlights for 3D Printer (Octoprint server)
A Python script sends an HTTP GET request to the octoprint server. If it responds that it is printing, a signal is sent to a relay that turns on a parallel led lamp that I use as a flood light for the timelapse camera.

## Requirements
### Software
* Python 3 (Should be installed by default on Raspbian - [How to install](https://www.raspberrypi.org/forums/viewtopic.php?t=181480)) 
* Python 3 RPi.GPIO package ```sudo pip install RPi.GPIO```
* Works fine on Raspbian Bullseye (Debian 11)

### Hardware
* Raspberry Pi
* 1 Channel 5V Relay [(Something like this)](https://www.amazon.com/dp/B00VRUAHLE/)
* A breadboard
* Some components (wires, LEDs and a resistor) to make the lamp

## Wiring scheme
There are two ways to wire this thing.
The first one is the reccommended way.
The second one is an alternate way if you are using a fan on your Pi alongside these LEDs and don't have any spare 5V pins.
In any case, wiring is fairly straight-forward. 

### Common parts
#### LEDs
1. Put 5 LEDs on the breadboard
1. Connect them in parallel (something like in the pictures below)
1. Add a 10Ω resistor on one side (in this case I put it on the positive side - red wires in the images below)
1. Connect a wire from the resistor to a 5V pin on your Raspberry Pi (red wire going from the breadbord to the Raspberry Pi in the images below)

#### Relay
1. Connect the NO to the negative side of the lamp (check the pictures below, it's the cyan wire going from the relay to the breadbord)
1. Connsct the signal pin on the relay to pin 7 on the Raspberry Pi (check the pictures below, it's the cyan wire going from the Raspberry Pi to the relay)
1. connect the - pin on the relay to a ground header on your Raspberry Pi
1. Connect the COM to another ground header on your raspberry Pi

### 1 - Default
![Wiring scheme](https://github.com/StoKatze/Automatic-Floodlights-For-3D-Printer-Octoprint-server-/blob/main/Wiring%20Scheme/Lampadina%20Stampante%203D_bb_normal.png)
* Connect the + pin on the relay to the other unused 5V pin on your Raspberry Pi (red wire going from the Raspberry Pi to the relay in the picvure above)
If you don't have a second 5V pin available, please follow the alternate wiring instructions.

### 2 - Alternate
![Wiring scheme Alternate](https://github.com/StoKatze/Automatic-Floodlights-For-3D-Printer-Octoprint-server-/blob/main/Wiring%20Scheme/Lampadina%20Stampante%203D_alternate.png)
* Connect the + pin on the relay to a 3.3V pin on your Raspberry Pi (white cable in the picture above)
Please note that if you have a fan, the ground pin next to the 5V one might be already occupied. This is not an issue since you can use any other ground pin.

## Usage 
Download the python script inside a directory, edit some parameters and execute it.
If your Octoprint server automatically starts at boot time, you can use a crontab to start this other script too.
If you want to use cron, I suggest setting it to run the autostart scripts. It's also possible to just run the python code directly if you don't want useless files in your system.

### Detailed instructions
#### Configuring the python script
1. Create a new directory and ```CD``` into it
1. Download [AutomaticOctoprintLED.py](Python/AutomaticOctoprintLED.py) in this directory
1. Edit it using nano or any other text editor ```nano AutomaticOctoprintLED.py```
1. Check and, if needed, edit your settings from line 13 to line 16 (an in-depth explaination of this option is available in the script, comments from line 6 to line 12)
1. Set your API Key on line 18 (Octoprint Server Web UI -> Settings -> API -> Enable CORS, then copy the Global API Key string) - DO NOT SHARE THIS KEY! WHOEVER HAS IT CAN CANTROL YOUR WHOLE OCTOPRINT SERVER!
1. If you are using another pin for the relay signal, edit line 23 too
1. Save and exit

#### Running the script manually
1. Execute the script ```python3 AutomaticOctoprintLED.py```
1. The script should print some text
1. Use ```CTRL+C``` to terminate it
1. OPTIONAL: you can run it to save a log file (don't forget the -u option - also note that the log is erased every time you start the python script) ```python3 -u AutomaticOctoprintLED.py > ./log.txt 2>&1 ``` or ignore all output ```python3 AutomaticOctoprintLED.py &> /dev/null``` - You can also use screen to hide the output (```sudo apt update && sudo apt install screen && screen``` press enter and write your command. You can use ```CTRL+A+D``` to detach from your screen session and ```screen -r``` to resume it)

####  Using the autostart with logging
1. Download the [octoprintLedLog.sh](Autostart/octoprintLedLog.sh) script in the same directory of the python file
1. Make it executable ```chmod +x octoprintLedLog.sh```
1. Execute it
Please note that the log file is erased every time you start this script.

#### Using the silent autostart
1. Download the [octoprintLed.sh](Autostart/octoprintLed.sh) file
1. Make it executable
1. Execute it

#### Using crontab to automatically start this script at boot time
1. Edit your user's crontab (don't forget to edit the path to match your system settings - also if you want to save a log file make sure that the user you're editing the crontab is allowed to write to the script folder): ```crontab -e```
* If using the logging start script [octoprintLedLog.sh](Autostart/octoprintLedLog.sh):<br>
```@reboot /path/to/your/octoprintLedLog.sh```
* If using the silent start script [octoprintLed.sh](Autostart/octoprintLed.sh):<br>
```@reboot /path/to/your/octoprintLed.sh```
* Or you can execute the python script directly (not tested but should work fine - not logging version):<br>
```@reboot python3 path/to/your/AutomaticOctoprintLED.py >& /dev/null```
* Or you can execute the python script directly (not tested but should work fine - logging version):<br>
```@reboot python3 path/to/your/AutomaticOctoprintLED.py > ./log.txt 2>&1```

If the script terminates earlier than expected (due to some connection errors) you may need to add some timeout to allow octoprint to start.
Just add ```sleep [NUMBER_IN_SECONDS] && `` after ```@reboot``` but before anything else (please note there must be a space after ```@reboot@ and after ```&&```).
E.g.: ```@reboot sleep 60 && /path/to/your/octoprintLed.sh``` [OR] ```@reboot sleep 120 && python3 path/to/your/AutomaticOctoprintLED.py > ./log.txt 2>&1```

## Thank you
I don't know much about electronics so I tried making this circuit as easy as possible. Suggestions are welcome.
