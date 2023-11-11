# HydroPico Webapp

The Hydro Pico web application allows you to complete the inital setup of your garden. Once the intial setup has been complete, the webapp allows you to monitor the garden, observe the sensor data, or initiate a reset of the garden. It runs on a Microdot Web Framework, and will run automatically on port 5000 when a network connection is established

## Network Setup

#### \*\*\*TODO OLED ROTARY ENCODER LOGIN

- SSID and Password Entry will be made available upon setup through the oled screen and rotary encoder. for now ...

For the intial network setup you will need to open up Thonny, or your Pico develpment environment of choice. Plug the pico into USB, if a config.bin file is not found, the network login function will launch automatically. Enter your network SSID along with your password. Your SSID and Password will be saved in encrypted form in a config.bin file for future logins. The webapp will start running automatically on port 5000.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_network_login.png" alt="HydroPico - network setup" width="600" />
</p>

The device IP address assigned by your network will be displayed once you are connected. In this case '192.168.5.97'

Enter 192.168.5.97:5000 into your web browser to access the web app

## Setup Screen

When the web application initially loads it will display the plant options, as laid out in the garden_data.py file, which holds in json format the data for the different plant options(name, pump intervals, temperature requirements, etc.)

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_setup.png" alt="HydroPico - setup screen" width="600" />
</p>

In this case the options are Tomato, Lettuce, and Basil. Select the option that you have planted in the garden, and your garden will begin.

## Live Garden Status

Once an option has been selected, the screen for the web application will reload. On one side you'll see a picture of the plant option selected, on the other side a placeholder photo for the live garden picture. The Airpump will turn on when the garden starts, along with the waterpump for the initial watering.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_soon.png" alt="HydroPico - garden status" width="600" />
</p>

The ON/OFF status of the pumps and heater are displayed, with a red background when on. This is set to update every 5 seconds, which can be updated in the index.js file. The number of days planted is displayed at the bottom of the screen.

## Garden Photo

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_garden.png" alt="HydroPico - garden photo" width="600" />
</p>

Once the Arducam has had the opportunity to take a picture of the garden, it will replace the placeholder photo on the right hand side. Transmitting the photo can be resource intensive, so to avoid any potential memory issues I don't want it to run automatically on startup. I set an inital delay of one minute before the garden takes it's first photo, which can be adjusted in the main loop in main.py.

## Live Sensor Readings

If you scroll down to the bottom of the page you'll see live sensor data displayed. This is set to update every 5 seconds, which can be updated in the index.js file.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_sensors.png" alt="HydroPico - sensor readings" width="600" />
</p>

At the top you'll see the "Click for more Sensor Data" button, and "Reset Garden" at the bottom. If you click "Reset Garden" the garden will reboot. Once it has rebooted, you will find the web application loadsto the intial Setup Screen wher you choose the plant type.

## Charts and Data

"Click for More Sensor Data" loads the sensor data graphs and gauges, provided by plotly.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_data.png" alt="HydroPico - data plotly" width="600" />
</p>

This is set to display data based on the last 24 data points, which can be updated in the data.js file.
