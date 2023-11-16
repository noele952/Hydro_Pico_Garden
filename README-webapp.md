# HydroPico Webapp

The Hydro Pico web application allows you to select a plant, and complete the inital setup of your garden. Once setup is complete, the webapp allows you to monitor the garden, observe the sensor data, or initiate a reset of the garden. It runs on a Microdot Web Framework, and will run automatically on port 5000 when a network connection is established

## Setup Screen

When the web application initially loads it will display the plant options, as laid out in the [garden_data](./data/garden_data.py) file, which holds operational data for the different plant options(name, pump intervals, temperature requirements, etc.)

You can modify the parameters, and add new plant options. The web application setup screen automatically populates based on the available options in the [garden_data](./data/garden_data.py) file. For each plant option, just place an identically named .jpg image in the /static/image folder.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_setup.png" alt="HydroPico - setup screen" width="600" />
</p>

In this case the options are Tomato, Lettuce, and Basil. Select your preferred option, and the garden will begin.

## Live Garden Status

Once an option has been selected, the web application screen will reload. On the left will be an image of the selected plant option, on the right, a placeholder for the live garden image. The Airpump will turn on when the garden starts, along with the waterpump for the initial watering.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_soon.png" alt="HydroPico - garden status" width="600" />
</p>

The ON/OFF status of the pumps and heater are displayed, with a red background when on. This is set to update every 5 seconds, which can be updated in the index.js file. The number of days planted is displayed at the bottom of the screen.

## Garden Photo

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_garden.png" alt="HydroPico - garden photo" width="600" />
</p>

Once the Arducam has had the opportunity to take a picture, it will replace the placeholder image of the garden. Transmitting the photo can be resource intensive, so to avoid any potential memory issues on startup, I set an inital delay of one minute before the garden first image is taken. This can be adjusted in the main loop in [main.py](main.py).

## Live Sensor Readings

Live sensor data is displayed at the bottom of the page. This is set to update every 5 seconds, which can be updated in the [index.js](./static/index.js) file.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_sensors.png" alt="HydroPico - sensor readings" width="600" />
</p>

At the top you'll see the "Click for more Sensor Data" button, and "Reset Garden" at the bottom. If you click "Reset Garden" the garden will reset and reboot .

## Charts and Data

"Click for More Sensor Data" loads the sensor data graphs and gauges, provided by plotly.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_data.png" alt="HydroPico - data plotly" width="600" />
</p>

This will display graphs based on the last 24 data points. This can be adjusted in the [data.js](./static/data.js) file.
