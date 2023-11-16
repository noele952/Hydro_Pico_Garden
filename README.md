<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPicoBanner.jpg" alt="hydro pico airpump" width="800" />
</p>

# HydroPico Hydroponic Garden

## Introduction

Welcome to the documentation for the HydroPico hydroponic Garden project. The HydroPico garden is designed to serve two purposes

**Garden Control System:**
The core focus lies in automating your gardening experience. Intelligently managing pumps and heating elements, in coordination with sensors, to optimize the growing environment. These settings are stored in a [garden_data](./data/garden_data.py) file, and are completely customizable.

Fine tune the parameters in the file(pump schedules, water heat, etc.), tailoring the environment to the specific requirements of any plant you choose to cultivate.

**IoT Data Collection Device:**
The second focus of the HydroPico garden is as an Internet of Things (IoT) data collecting device. Connecting to AWS IoT Core, it logs the sensor data to a DynamoDB table and captures hourly snapshots of the garden. You can connect as many gardens as you want to a single AWS IoT core account, and all of the data for each individual garden will be separated and stored.

The images, coupled with real-time sensor data, can be accessed within a web application, hosted on your local network by the HydroPico garden. Much of this data can be accessed from an attached oled screen as well.

Looking ahead, the collected data and images hold promise for potential machine learning applications—analyzing growth patterns, predicting harvest times, estimating yields, or identifying plant nutrition issues.

### Future Enhancements

The HydroPico Garden project is continuously evolving. Here are some planned enhancements for the future:

- **Capacitive Fluid Level Sensor:**
  Build a capacitive fluid level sensor that measures and reports the depth of the water using a submerged capacitor, using the different dielectric properties of water and air to measure the level.

- **LED Grow Light Integration:**
  Incorporate LED grow lights into the HydroPico Garden to enhance the growth conditions for the plant.

## Table of Contents

1. [Introduction](#introduction)
2. [Hardware Setup](#hardware-setup)
3. [Software Dependencies](#dependencies)
4. [Installation](#installation)
5. [Garden Construction](#garden-construction)
6. [Web Application](#web-application)
7. [Usage](#usage)
8. [Contributions](#contributions)
9. [Media](#media)
10. [License](#license)

## Hardware Setup

I've included a bill of materials for the hardware, and a complete wiring schematic below. It all fits on a 7x9cm PCB Prototype Board.

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/garden_pcb.jpg" alt="hydro pico wiring diagram - complete" width="400" />
</p>
<h2>Bill of Materials (BOM)</h2>

1. **Raspberry Pi Pico W Microcontroller**

   - [Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
   - [Purchase on Amazon](https://www.amazon.com/Raspberry-Pico-Bluetooth-Beginner-Friendly-microcontroller/dp/B0C4TRR6VT/ref=sr_1_5?crid=2CUWXB5HDX9RC&keywords=pi+pico+w&qid=1699369099&sprefix=pi+pcio+w%2Caps%2C157&sr=8-5)

2. **BME280 Environmental Sensor**

   - [Datasheet](https://www.mouser.com/datasheet/2/783/BST-BME280-DS002-1509607.pdf)
   - [Purchase on Amazon](https://www.amazon.com/HiLetgo-Atmospheric-Pressure-Temperature-Humidity/dp/B01N47LZ4P/ref=sr_1_3_pp?crid=OD2RGI8H5ZZ7&keywords=bme280&qid=1699369713&sprefix=bme280%2Caps%2C147&sr=8-3)

3. **SSD1306 OLED Screen I2C 128x64**

   - [Datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf)
   - [Purchase on Amazon](https://www.amazon.com/Hosyond-Display-Self-Luminous-Compatible-Raspberry/dp/B09T6SJBV5/ref=sr_1_1?crid=E79PNJ43RVOL&keywords=Hosyond+5+Pcs+0.96+Inch+OLED+I2C+IIC+Display+Module+12864&qid=1699369884&s=electronics&sprefix=hosyond+5+pcs+0.96+inch+oled+i2c+iic+display+module+12864%2Celectronics%2C165&sr=1-1)

4. **Dual MOSFET PWM Switch Module 5V-36V 15A 400W**

   - Quantity: 3
   - [Datasheet](https://michiel.vanderwulp.be/domotica/Modules/MosFetPwmDriveModule/#product-parameters-and-application-1)
   - [Purchase on Amazon](<https://www.amazon.com/Anmbest-High-Power-Adjustment-Electronic-Brightness/dp/B07NWD8W26/ref=sr_1_2?crid=2WVQVHXJHKII5&keywords=Anmbest%2B5PCS%2BDC%2B5V-36V%2B15A(Max%2B30A)%2B400W%2BDual%2BHigh-Power%2BMOSFET%2BTrigger%2BSwitch%2BDrive%2BModule&qid=1699370554&sprefix=anmbest%2B5pcs%2Bdc%2B5v-36v%2B15a%2Bmax%2B30a%2B400w%2Bdual%2Bhigh-power%2Bmosfet%2Btrigger%2Bswitch%2Bdrive%2Bmodul%2Caps%2C174&sr=8-2&th=1>)

5. **LM2596S Input 3.0-40V Output 1.5-35V Adjustable Buck Converter**

   - [Datasheet](https://www.ti.com/lit/ds/symlink/lm2596.pdf?ts=1699371331070&ref_url=https%253A%252F%252Fwww.google.com%252F)
   - [Purchase on Amazon](https://www.amazon.com/Regulator-Adjustable-Converter-Electronic-Stabilizer/dp/B07PDGG84B/ref=sr_1_3?crid=13XTYET0MV0B1&keywords=LM2596S+DC-DC+Step+Down+Variable+Volt+Regulator+Input+3.0-40V+Output+1.5-35V+Adjustable+Buck+Converte&qid=1699371412&sprefix=lm2596s+dc-dc+step+down+variable+volt+regulator+input+3.0-40v+output+1.5-35v+adjustable+buck+converte%2Caps%2C340&sr=8-3)

6. **ArduCam Mega SPI Camera 5MP**

   - [Datasheet](https://www.arducam.com/wp-content/uploads/2023/10/Arducam-MEGA-DATASHEET.pdf)
   - [Purchase on Amazon](https://www.amazon.com/Arducam-Mega-Camera-Module-Microcontroller/dp/B0BW7MDVHK/ref=sr_1_2?crid=3CLOW2AOH3ZSG&keywords=Arducam+for+Arduino+Camera+Module%2C+5MP+Autofocus+SPI+Camera&qid=1699370358&s=electronics&sprefix=arducam+for+arduino+camera+module%2C+5mp+autofocus+spi+camera%2Celectronics%2C151&sr=1-2)

7. **KY-040 Rotary Encoder**

   - [Datasheet](https://components101.com/sites/default/files/component_datasheet/KY-04-Rotary-Encoder-Datasheet.pdf)
   - [Purchase on Amazon](https://www.amazon.com/Taiss-KY-040-Encoder-15%C3%9716-5-Arduino/dp/B07F26CT6B/ref=sr_1_1_pp?crid=30QW4QLNITSU4&keywords=KY-040+Rotary+Encoder&qid=1699371674&sprefix=ky-040+rotary+encoder%2Caps%2C263&sr=8-1)

8. **Polyimide Heater Pad 12V 13W Adhesive Round 70mm**

   - [Documentation](https://laminatedplastics.com/polyimide.pdf)
   - [Purchase on Amazon](https://www.amazon.com/12V-Flexible-Polyimide-Heater-Plate/dp/B07P1H8N8H/ref=sr_1_2?crid=23M5YR601IV0S&keywords=Film%2BHeater%2BPlate%2BAdhesive%2BPad%2C%2BIcstation%2BPI%2BHeating%2BElements%2BFilm%2BRound%2B12V%2B13W%2BAdhesive%2BPolyimide%2BHeater%2BPlate%2B70mm&qid=1699372529&sprefix=film%2Bheater%2Bplate%2Badhesive%2Bpad%2C%2Bicstation%2Bpi%2Bheating%2Belements%2Bfilm%2Bround%2B12v%2B13w%2Badhesive%2Bpolyimide%2Bheater%2Bplate%2B70mm%2Caps%2C384&sr=8-2&th=1)

9. **Mini Air Pump 3V DC**

   - [Purchase on Amazon](https://www.amazon.com/dp/B08SCHXN2Z?psc=1&ref=ppx_yo2ov_dt_b_product_details)

10. **Water Pump Submersible 10L/Min 600L/H DC 12V 1.2A 5M High**

    - [Purchase on Amazon](https://www.amazon.com/dp/B01MRR4HGK?psc=1&ref=ppx_yo2ov_dt_b_product_details)

### Wiring Diagram

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/hydro_pico_bb.png" alt="hydro pico wiring diagram - complete" width="600" />
</p>
<h2>HydroPico Wiring Diagram - Complete</h2>

This is the complete HydroPico wiring diagram, click the links below for wiring diagrams divided into sub systems, with detailed explanations.

[HydroPico Wiring Diagram - Power](#power-supply)

[HydroPico Wiring Diagram - Screen and Encoder](#oled-screen-and-encoder)

[HydroPico Wiring Diagram - Sensors and Camera](#sensors-and-camera)

### Hardware Test

Before starting your garden, it's recommended to run a hardware test to ensure all components are assembled correctly and functioning properly.

First, install the [Software Dependencies](#dependencies) below.

Once you have the hardware libraries installed, run the
[hardware_test.py](./tests/hardware_test.py) file, located in the /tests folder. You can see a succsesful test in the video below.

#### Hardware Test -> Click For Video

[![Alt text](https://img.youtube.com/vi/kN2_r-vspps/0.jpg)](https://www.youtube.com/watch?v=kN2_r-vspps)

## Dependencies

### Software Dependencies

Install the following Micropythonlibraries on the pico w microcontroller

- [Microdot GitHub](https://github.com/miguelgrinberg/microdot)

- [Microdot_uTemplate GitHub](https://github.com/miguelgrinberg/microdot)

- [SSD1306 Driver GitHub](https://github.com/noele952/micropython-ssd1306-custom-text/blob/main/ssd1306.py)

- [Rotary Encoder Driver GitHub](https://github.com/MikeTeachman/micropython-rotary)

- [BME280 Driver GitHub](https://github.com/bilalmalik76/MicroPython-BME280-Web-Server-with-ESP32-ESP8266-Weather-Station-/blob/main/BME280.py)

- [umqtt.simple GitHub](https://github.com/fizista/micropython-umqtt.simple2)

- [Arducam MicroPython Driver GitHub](https://github.com/CoreElectronics/CE-Arducam-MicroPython)

### AWS Prerequisites

We also have a few Amazon Web Services dependencies that the HydroPico garden will require. First, we will need to establish a secure connection to AWS IoT Core so that we can send in MQTT data. Second we'll need to create Lambda functions to process that mqtt data. And third we'll need to create a few IoT core message routing rules, so we can make sure that data gets processed by the proper Lambda function, depending on the type of the data(sensor, image, etc.)

#### Automated Deployment (Optional)

To streamline the AWS asset deployment, use our CloudFormation template:

[CloudFormation Template](./infrastructure/cloudformation/cloudformation.yaml)

The Security Certicate must be created manually, but otherwise you can skip most of the steps below. After you deploy the CloudFormation stack, go to step 4 and create the certificate, ignore the rest of the steps(Lambda, AWS IoT) unless they pertain to that certificate

#### AWS IoT Core Security

Before you can connect to AWS IoT, you will need to to generate a security certificate, and a key. Follow these steps to get set this up with AWS IoT Core:

\* The AWS interface is subject to change at any time. You may need to adapt these instructions

1. **Step 1:** Connect to AWS and open IoT Core
2. **Step 2:** From the AWS IoT menu select Security > Policies
3. **Step 3:** From the policies menu select create policy, add the following policy statements, and click create

- Allow - iot:Connect - \*
- Allow - iot:Publish - \*
- Allow - iot:Receive - \*
- Allow - iot:Subscribe - \*

4. **Step 4:** In the security > certificates menu, click Add Certificate, then select Create Certificate
5. **Step 5:** Select Auto Generate then click Create, and download the certificates

   \*\*\*BE AWARE - this is the only time they will be available for download

6. **Step 6:** Go to AWS IoT > Manage > Things and click Create Things
7. **Step 7:** select Create single thing, select No shadow, and name the thing. Skip certificate creation
8. **Step 8:** In Security > Certificates menu, select the certificate created in step 5, click Attach policies, and attach the policy created in step 3

9. **Step 9:** in the certificate menu, select Things, click Attach to things, and attach the thing you created in step 7

10. **Step 10:** Go to the Settings Menu, and copy the Endpoint. In the config.py file set your MQTT_CLIENT_ID to the Endpoint value

Now we need to convert the key and certificate to DER format, and store it on your pico.

To complete the conversion you will need to have openssl installed. In a terminal run the following commands on the key and certificate files that you downloaded previously.

```
openssl rsa -in private.pem.key -out private.der - outform DER

openssl x509 -in certificate.pem.crt -out certificate.der -outform DER
```

Take the certificates and store them in the /certs folder on the pico.

The name and placement of your certificate and key files can be adjusted in config.py by changing the value of CERT_FILE and KEY_FILE

#### AWS LAMBDA

Now that we have an MQTT connection, we need some Lambda functions to process the messages. Consult the README.md file attached to each function for further instructions.

The first function processes the sensor data messages, and saves the data in a DynamoDB table.

[collect_data_mqtt](https://github.com/noele952/Lambda_collect_mqtt_data)

In order to send the garden picture jpeg file over MQTT, it is first broken down into a series of 64 bit encoded strings, which are then sent as a series of mqtt messages. The second link is a pair of Lambda functions. The first function takes the encoded strings and stores them together in a DynamoDB table. The second reassembles the pieces into a .jpeg file, and places it in your garden picture S3 bucket.

[transmit_pic_mqtt](https://github.com/noele952/Lambda_transmit_pic_mqtt)

#### AWS IoT Core Message Routing

With a secure AWS Iot Core connectionsetup, and Lambda functions to process the messages, we now need to setup AWS IoT Core messaging rules to send the messages to the proper Lambda functions:

1. **Step 1:** Open AWS IoT Core, from Message routing > Rules select Create Rule
2. **Step 2:** Name the rule whatever you like, and supply this SQL statement:

```
SELECT \* FROM 'GardenData' WHERE label = 'data'
```

3. **Step 3:** For Rule Action select Lambda, then select the [collect_data_mqtt](https://github.com/noele952/Lambda_collect_mqtt_data) Lambda function created previously
4. **Step 4:** create another rule, and supply this SQL statement:

```
SELECT \* FROM 'GardenData' WHERE label = 'garden_pic'
```

5. **Step 5:** For Rule Action, select Lambda, then select the [store_mqtt_pic](https://github.com/noele952/Lambda_collect_mqtt_data) Lambda function created previously

With the AWS configuration complete, we can finish setting up the garden.

## Installation

If the AWS prerequisites are completed, and the software dependencies are installed, just clone the github repository and install on the Pico W.

Plug in the power supply, and follow the instructions on the oled screen to get the HydroPico garden connected to your network.

#### HydroPico Setup -> Click For Video

[![Alt text](https://img.youtube.com/vi/FqmGYAr5RJ0/0.jpg)](https://www.youtube.com/watch?v=FqmGYAr5RJ0)

### Configuration

There are a few configuration options available in the config.py file. If you are running only one garden, no configuration is necessary.

from config.py:

```python
        self.AES_CIPHER = b'1234567890123456'
        self.MACHINE_ID = 'machine_id'
        self.CERT_FILE = '/certs/certificate.der'
        self.KEY_FILE = '/certs/private.der'
        self.IMAGE_FILE = '/static/images/image.jpg'
        self.CLOUD_IMAGE_PREFIX = 'garden_pic'
        self.MQTT_CHUNK_SIZE=1536
```

AES_CIPHER is used to encrypt/decrypt your network password, for security. Feel free to customize, must be 16 digits

MACHINE_ID is used to label the MQTT data. If runnning multiple gardens, give them a unique MACHINE_ID and their data will be stored seperately.

CERT_FILE and KEY_FILE can be altered if you'd like to change the name/location of your AWS IoT Core certificate and key file.

MQTT_CHUNK_SIZE determines the length of the 64 bit encoded strings that the garden photo jpeg file is broken into before sending. Adjust at your own risk. The larger the chunk, the fewer the messages that need to be sent, but the greater the potential for memory issues.

Consult the [Web Application](README-webapp.md) section for instructions in that regard.

## Garden Construction

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/garden_complete.jpg" alt="hydro pico wiring diagram - power supply" height="400" />
</p>

For detailed information about constructing the garden, please refer to the [Garden Construction README](README-construction.md).

## Web Application

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/HydroPico_webapp_garden.png" alt="HydroPico - garden photo" width="300" />
</p>

For detailed information about setting up and running the web app, please refer to the [Web App Section README](README-webapp.md).

## Usage

Once you have your garden started everything is automated. Just keep ithe bucket filled with the nutrient solution of your choice. I recommend [General Hydroponics](https://www.amazon.com/General-Hydroponics-FloraSeries-Hydroponic-Fertilizer/dp/B0B2C22L3G/ref=sr_1_5?crid=OJRH8ZP8J8AK&keywords=general%2Bhydroponics&qid=1699503106&sprefix=general%2Bhydroponics%2Caps%2C162&sr=8-5&th=1)

Refer to the [Web Application Section](README-webapp.md) for details on using the web application. You can also interface with the machine through the oled screen and the rotary encoder.

#### OLED Main Menu -> Click For Video

[![Alt text](https://img.youtube.com/vi/PLSq3jq0oMs/0.jpg)](https://www.youtube.com/watch?v=PLSq3jq0oMs)

## Media

### Power Supply

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/hydro_pico_power_bb.png" alt="hydro pico wiring diagram - power supply" width="600" />
</p>

For power supply we use a 12V DC Adapter. That gets routed to the IN+ and IN- of the buck convertor, and the MOSFET trigger switches for the waterpump and the heater.

From the buck convertor, connect OUT- to ground on the Pico, and OUT+ to the VSYS Pin on the Pico(39). A 1N5817 diode is wired inline as a "diode ORing". This ensures there is no current backflow if the Pico is connected to both the DC power and the built in USB power simultaneously. For example, when connecting the pico to a PC.

Connect OUT+ and OUT- from the buck convertor to the MOSFET trigger switch for the airpump, which also uses 3.3V power.

The airpump and waterpump MOSFET trigger switches have a simple on/off function. We use Pin GP22 for the airpump, and GP4 for the waterpump.

For the heater we'll need Pulse Width Modulation(PWM), giving us the ability to vary the heater power from high to low. Connect the heaters MOSFET trigger switch to GP28.

The power outputs are connected to dupont pins soldered to the PCB board, with the corresponding dupont connectors attached to wiring for the airpump, waterpump, and heater.

### OLED Screen and Encoder

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/hydro_pico_screen_bb.png" alt="hydro pico wiring diagram - screen and enocoder" width="400" />
</p>

The OLED screen connects via I2C. The I2C bus connects to I2C Channel 1 on pins GP6 and GP7. 10K Ω pullup resistors connect the I2C data and clock lines to power, for voltage stability.

For the Rotary Encoder we connect Clock(CLK) to GP11, Data(DT) to GP10, and Switch(SW) to GP12

### Sensors and Camera

<p align="center">
<img src="https://hydropi.s3.us-east-2.amazonaws.com/github/hydro_pico_sensors_bb.png" alt="hydro pico wiring diagram - sensors and camera" width="600" />
</p>

The BME280 breakout board collects temperature, humidity and barometric pressure data. It connects via I2C,on GP6 and GP7. We setup the I2C bus in the OLED screen section above.

The Photoresistor (LDR) provides light level data. It provides an analog signal and requires an ADC (Analog-to-Digital Convertor) pin. In this case GP27. A 10k Ω pull-down resistor pulls the signal low when the line is idle.

A Thermistor is submerged in the nutrient solution to provide water data. See the [Garden Construction README](README-construction.md) for details.
It provides an analog signal and requires an ADC (Analog-to-Digital Convertor) pin. In this case GP26. A 10k Ω pull-up resistor pulls the signal high when the line is idle.

For the ArduCam MEGA SPI 5MP camera connect Serial Clock(SCK) to GP18, MISO to GP16, MOSI to GP19, and Chip Select(CS) on GP17.

## Contributions

Feel free to contribute by reporting issues or submitting pull requests.

A project like the Hydroponic Garden wouldn't be possible without the valuable contributions of various libraries and drivers:

### Web Framework and Templating Engine

- **Microdot (microdot_asyncio):**

  - [Microdot GitHub](https://github.com/miguelgrinberg/microdot)

- **Microdot_uTemplate:**
  - [Microdot_uTemplate GitHub](https://github.com/miguelgrinberg/microdot)

### Rotary Encoder Driver

- **Rotary Encoder Driver:**
  - [Rotary Encoder Driver GitHub](https://github.com/MikeTeachman/micropython-rotary)

### Environmental Sensor Driver

- **BME280 Driver:**
  - [BME280 Driver GitHub](https://github.com/bilalmalik76/MicroPython-BME280-Web-Server-with-ESP32-ESP8266-Weather-Station-/blob/main/BME280.py)

### MQTT Connection

- **umqtt.simple:**
  - [umqtt.simple GitHub](https://github.com/fizista/micropython-umqtt.simple2)

### Camera Driver

- **Arducam MicroPython Driver:**
  - [Arducam MicroPython Driver GitHub](https://github.com/CoreElectronics/CE-Arducam-MicroPython)

## License

This DynamoDB Picture Assembly System is licensed under the [MIT License](LICENSE).
