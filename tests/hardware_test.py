from config import ConfigManager
from machine import Pin, I2C, ADC, SPI
import ssd1306
import bme280
from rotary_irq_pico import RotaryIRQ
from camera import Camera
import os
import time
import math

# Create config, which will load hardware pin values, among other config data
app_config = ConfigManager(filename='testing')

# Configure attached hardware
led = Pin(app_config.LED_PIN, Pin.OUT)
i2c = I2C(app_config.I2C_CHANNEL, sda=Pin(app_config.I2C_DATA), scl=Pin(app_config.I2C_CLOCK))
oled = ssd1306.SSD1306_I2C(app_config.OLED_WIDTH,app_config.OLED_HEIGHT, i2c)
rotary_button = Pin(app_config.R_BTN_PIN, Pin.IN, Pin.PULL_UP)
rotary_knob = RotaryIRQ(app_config.R_CL_PIN,
                        app_config.R_DT_PIN,
                        reverse=False, min_val=0,
                        max_val=9,
                        incr=1,
                        range_mode=RotaryIRQ.RANGE_WRAP,
                        pull_up=True,
                        half_step=False)

cam = Camera(SPI(0,sck=Pin(app_config.CAM_SCK), miso=Pin(app_config.CAM_MISO), mosi=Pin(app_config.CAM_MOSI)), Pin(app_config.CAM_CS, Pin.OUT))

# Configure switches
airpump = Pin(app_config.APUMP_PIN, Pin.OUT)
waterpump = Pin(app_config.WPUMP_PIN, Pin.OUT)
heater = Pin(app_config.HEATER_PIN, Pin.OUT) 

# Configure sensors
thermistor = ADC(app_config.THERM_PIN)
photoresistor = ADC(app_config.PHOTORES_PIN)
bme = bme280.BME280(i2c=i2c) # environmental sensor (temp, pres, hum)


def display_text(line1='', line2='', line3='', line4=''):
    # Display text to oled screen, up to 4 lines
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 16)
    oled.text(line3, 0, 32)
    oled.text(line4, 0, 48)
    oled.show()


def photoresistor_percent():
    # Return str light level a percentage based on ADC value of 0-65535 '{pct} %'
    photo_value = photoresistor.read_u16()
    light_percentage = str(round(photo_value/65535*100, 2)) + '%'
    return light_percentage

def thermistor_temp():
    # Return str temperature in Celsius, '{temp} C'
    adc = thermistor.read_u16()
    Vout = (3.3/65535)*adc
    # Voltage Divider
    Vin = 3.3
    Ro = 10000  # 10k Resistor
    # Steinhart Constants
    A = 0.001129148
    B = 0.000234125
    C = 0.0000000876741
    # Calculate Resistance
    Rt = (Vout * Ro) / (Vin - Vout)
    # Steinhart - Hart Equation
    temp_k = 1 / (A + (B * math.log(Rt)) + C * math.pow(math.log(Rt), 3))
    temp_c = f'{round(temp_k - 273.15, 1)} C'
    return temp_c

# Define a list of sensor data tuples, each containing a name and a corresponding function to retrieve data
sensors = [
    ("Temperature", bme.temperature),
    ("Barometer", bme.pressure),
    ("Humidity", bme.humidity),
    ("Thermistor", thermistor_temp()),
    ("Photoresistor", photoresistor_percent())
]

# Define a list of switch control tuples, each containing a name and the corresponding switch object
switches = [
    ("Airpump", airpump),
    ("Waterpump", waterpump),
    ("Heater", heater)
]


# Scan for connected I2C devices and sdisplay to terminal
devices = i2c.scan()
print("I2C Devices Found: ")
for device in devices:
        print("Device Address: 0x{:02X}".format(device))

# Screen test, lights up all pixels on OLED
oled.fill(1)
oled.show()
time.sleep(1)

# Set initial values for rotary encoder
val_old = rotary_knob.value()
but_old = rotary_button.value()

display_text('EncoderTest', 'Turn to Test', 'Push to Finish')

active=True
while active:
    val_new = rotary_knob.value()
    but_new = rotary_button.value()

    # Rotary encoder test
    if val_old != val_new:
        val_old = val_new
        display_text('EncoderTest', 'Turn to Test', 'Push to Complete', f'step: {str(val_new)}')

    # Camera test
    if but_old != but_new:
        but_old = but_new
        display_text('Camera Test', 'Capturing Image')
        time.sleep(1)
        cam.capture_jpg()
        display_text('Camera Test', 'Image Captured', 'Saving...')
        time.sleep_ms(2000)
        cam.saveJPG('image.jpg')
        time.sleep(1)
        display_text()
        active =False


# Test sensors and switches, display values on oled
try:
    while True:
        for switch in switches:
            switch[1].on()
            led.value(not led.value())
            display_text("Switch Test", switch[0], "LIGHT ON")
            time.sleep(2)
            switch[1].off()
        
        for sensor in sensors:
            led.value(not led.value())
            display_text("Sensor Test", sensor[0], sensor[1], 'Ctrl C to End')
            time.sleep(2)

# Ctrl+c to end test, cleanup any files created  
except KeyboardInterrupt as e:
    print(e)
    led.off()
    display_text()
    if "testing" in os.listdir():
        os.remove("testing")
        print("Testing file deleted")
    if "image.jpg" in os.listdir():
        os.remove("image.jpg")
        print("Image file deleted")
   
    


