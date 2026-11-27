
# AirQuality Sensor

A project designed to monitor and display air quality data using a Raspberry Pi and compatible hardware. It gathers data such as particulate matter levels and displays the readings on screen. Additionally, the project includes a web interface for remote access to sensor data using a FastAPI server.

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Setup](#Setup)
   - [Setup Sensors](#setup-sensors)
   - [Setup Raspberry](#setup-raspberry)
3. [Installation](#installation)
   - [Cloning the Repository](#cloning-the-repository)
   - [Setting Up Virtual Environment](#setting-up-virtual-environment)
   - [Installing Dependencies](#installing-dependencies)
4. [Running the Project](#running-the-project)
    - [Autostart](#autostart)
5. [Further Instructions](#further-instructions)
6. [API Usage](#api-usage)

## Hardware

- **Raspberry PI 4** - https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
- **Hosyond 7 Inch Touchscreen IPS DSI Display** - https://www.amazon.com/Hosyond-Touchscreen-Compatible-Capacitive-Driver-Free/dp/B0D3QB7X4Z/ref=sr_1_3?sr=8-3
- **GPIO Edge Extension for Raspberry Pi** - https://thepihut.com/products/gpio-edge-extension-for-raspberry-pi
- **Enviro + Air Quality for Raspberry Pi** - https://thepihut.com/products/enviro-air-quality-for-raspberry-pi
- **PMS5003 Particulate Matter Sensor with Cable** - https://thepihut.com/products/pms5003-particulate-matter-sensor-with-cable

## Setup Sensors

**Enviro sensors assemblation video**: **https://www.youtube.com/watch?v=M2Y9n6fhoxI**

## Setup Raspberry
**Update your Raspberry**

```bash
sudo apt update
sudo apt full-upgrade
```

**Hardware configuration**

Open the config file:

```bash
sudo nano /boot/firmware/config.txt
```

Make sure these options are turned on:

```bash
dtparam=i2c_arm=on
dtparam=spi=on
display_auto_detect=1
```

In the bottom of the file write the following lines:

```bash
enable_uart=1
dtparam=spi=on
dtoverlay=waveshare35a
hdmi_force_hotplug=1
max_usb_current=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt 640 480 60 6 0 0 0
hdmi_drive=2
display_rotate=2
dtoverlay=pi3-miniuart-bt
```

## Installation

First clone the git repository to your computer:

**Clone the repository**


```bash
git clone git@github.com:username/Air-Quality.git
```
```bash 
cd Air-Quality
```

**Make a virtual environment**

Install python virtualenv if not already installed:

```bash
pip install virtualenv
```

**Linux/MacOS**

Create the virtualenv:

```bash
python3 -m venv .venv
```

replace the .venv with your desired name for the environment

Activate the virtual environment:

```bash
source .venv/bin/activate
```

**Windows**

Create the virtualenv:

```bash
python -m venv .venv
```

replace the .venv with your desired name for the environment

Activate the virtual environment:

```bash
venv\Scripts\activate
```

**Install dependancies**

```bash
pip install -r requirements.txt
```

## Run

If you did everything correct so far, and you have enabled your virtualenv, execute the `main.py` file.


```bash
python3 main.py
```

If you want the sensors to start automatically with the raspberry use the autostart folder.

```bash
cd .config/autostart
```

```bash
sudo nano air.desktop
```

```bash
sudo nano airweb.desktop
```

In the air.desktop file paste the following lines.

```bash
[Desktop Entry]
Type=Application
Name=Air
Exec=/PATH_TO_YOUR_PROJECT/air_quality/autostart/start_air_desktop.sh
```

> [!WARNING]
> Check the `.sh` files in the `autostart` folder and replace the project path and the `.venv` name with yours. 
>
> Otherwise it will not work!

If you want to the web page to start automatically too open the airweb.desktop file and paste the following lines:

```bash
[Desktop Entry]
Type=Application
Name=Air-Web
Exec=/PATH_TO_YOUR_PROJECT/air_quality/autostart/start_air_web.sh
```

**Check the .sh files in the autostart folder and raplace the project path and the .venv name with yours, otherwise it will not work!!!**

## Further Instructions

If everything works as expected you should see on your screen a cli interfaces showing:

- Date Title Clock on the top of the screen.
- 3 columns with 4 rows showing sensor data. (Keep in mind if you did not attach you sensors properly or did not install the dependancies from the requirements.txt file the sensors will show 0)
- In the bottom right of your screen there is the IP address of your raspberry

[![sensors.png](https://i.postimg.cc/MpRT8Yby/sensors.png)](https://postimg.cc/JsrmNZFn)

**Initiating a web server**

If lets say you want to check your sensor reading remotly in the project there is a simple **fastapi** localhost server.

- To start the web-server type the following command:

```bash
make web-start
```

- Then you can either type in the browser:

```bash
http://0.0.0.0:8000
```

or type the **IP Address** shown in the bottom right of your screen adding at the end the port **:8000**

[![web-sensors.png](https://i.postimg.cc/9fLj34Sd/web-sensors.png)](https://postimg.cc/DW4NLz70)

## API

If you want to use the sensor-data excluded from everything else you can go to:

```bash
http://0.0.0.0:8000/api/air-data
```

There you can see a json formatted data of all the data that the sensors are returning.
