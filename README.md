# AirQuality Sensor

This project is an Air Quality Sensor designed to monitor and display air quality data using a Raspberry Pi and compatible hardware. It gathers data such as particulate matter levels and displays the readings on a Waveshare screen. Additionally, the project includes a web interface for remote access to sensor data using a FastAPI server.

## Table of Contents

1. [Introduction](#introduction)
2. [Hardware Requirements](#hardware-requirements)
3. [Setup Raspberry Hardware](#setup-raspberry-hardware)
   - [Display Configuration](#display-configuration)
   - [Update Raspberry](#update-raspberry)
4. [Installation](#installation)
   - [Installing Git](#installing-git)
   - [Cloning the Repository](#cloning-the-repository)
   - [Setting Up Virtual Environment](#setting-up-virtual-environment)
   - [Installing Dependencies](#installing-dependencies)
5. [Running the Project](#running-the-project)
6. [Further Instructions](#further-instructions)
7. [API Usage](#api-usage)

## Hardware

- **Raspberry PI 4** - https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
- **Waveshare 4.3inch 480x320 display** - https://www.waveshare.com/4inch-rpi-lcd-a.htm
- **GPIO Edge Extension for Raspberry Pi** - https://thepihut.com/products/gpio-edge-extension-for-raspberry-pi
- **Enviro + Air Quality for Raspberry Pi** - https://thepihut.com/products/enviro-air-quality-for-raspberry-pi
- **PMS5003 Particulate Matter Sensor with Cable** - https://thepihut.com/products/pms5003-particulate-matter-sensor-with-cable

## Setup Raspberry hardware

**Dipslay configuration**

Skip if not having the same display!

- Documentation: https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A)_Manual_Configuration#For_All_Raspberry_Pi_Versions

**Enviro sensors assemblation video**:
https://www.youtube.com/watch?v=M2Y9n6fhoxI

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

If you do not have git installed:

**Ubuntu/Debian**

```bash
sudo apt update
sudo apt install git
```

**Fedora**

```bash
sudo dnf install git
```

**Arch Linux/Manjaro**

```bash
sudo pacman -S git
```

**MacOS**

Install Homebrew if not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```

Install git:

```bash
brew install git
```

**Windows**

Download git from the official site:
https://git-scm.com/download/win

**Clone the repository**
Copy the command from the green **code** button.

```bash
git clone git@github.com:username/Air-Quality.git
```

**Make a virtual environment**

Install virtualenv if not already installed:

```bash
pip install virtualenv
```

**Linux/MacOS**

Go to the folder:

```bash
cd Air-Quality/
```

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

Go to the folder:

```bash
cd Air-Quality/
```

Create the virtualenv:

```bash
python -m venv .venv
```

replace the .venv with your desired name for the environment

Activate the virtual environment:

```bash
venv\Scripts\activate
```

**Generate requirements.txt**

```bash
pip freeze > requirements.txt
```

**Install dependancies**

```bash
pip install -r requirements.txt
```

## Run

If you did everything correct so far, and you have enabled your virtualenv, everything is ready to run the main command in your project.

```bash
python3 main.py
```

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
