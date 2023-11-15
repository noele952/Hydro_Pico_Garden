from classes.config import ConfigManager
from machine import Pin, I2C, ADC, SPI
import ssd1306
import bme280
from rotary_irq_pico import RotaryIRQ
from camera import Camera
import os
import time
import math

I2C_CLOCK = 7
I2C_DATA = 6
I2C_CHANNEL = 1
APUMP_PIN = 22  
WPUMP_PIN = 4
PHOTORES_PIN = 27
HEATER_PIN = 28
LED_PIN = 15
THERM_PIN = 26
R_BTN_PIN = 12
R_CL_PIN = 11
R_DT_PIN = 10
CAM_SCK = 18
CAM_MISO = 16
CAM_MOSI = 19
CAM_CS = 17
OLED_WIDTH = 128
OLED_HEIGHT = 64

led = Pin(LED_PIN, Pin.OUT)
i2c = I2C(I2C_CHANNEL, sda=Pin(I2C_DATA), scl=Pin(I2C_CLOCK))

rotary_button = Pin(R_BTN_PIN, Pin.IN, Pin.PULL_UP)
rotary_knob = RotaryIRQ(R_CL_PIN, R_DT_PIN,reverse=False, min_val=0,
                        max_val=9,
                        incr=1,
                        range_mode=RotaryIRQ.RANGE_WRAP,
                        pull_up=True,
                        half_step=False)

cam = Camera(SPI(0,sck=Pin(CAM_SCK), miso=Pin(CAM_MISO), mosi=Pin(CAM_MOSI)), Pin(CAM_CS, Pin.OUT))

# switches
airpump = Pin(APUMP_PIN, Pin.OUT)
waterpump = Pin(WPUMP_PIN, Pin.OUT)
heater = Pin(HEATER_PIN, Pin.OUT) #PWM(Pin(heater_pin), freq=60, duty_u16=0) # duty_u16 sets the duty cycle as a ratio duty_u16 / 65535

# sensors
thermistor = ADC(THERM_PIN)
photoresistor = ADC(PHOTORES_PIN)
bme = bme280.BME280(i2c=i2c)       
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)



def display_test(line1='', line2='', line3='', line4=''):
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 16)
    oled.text(line3, 0, 32)
    oled.text(line4, 0, 48)
    oled.show()


def photoresistor_percent():
    photo_value = photoresistor.read_u16()
    light_percentage = str(round(photo_value/65535*100, 2)) + '%'
    return light_percentage

def thermistor_temp():
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

sensors = [("Temperature", bme.temperature), ("Barometer", bme.pressure), ("Humidity", bme.humidity), ("Thermistor", thermistor_temp()),
           ("Photoresistor", photoresistor_percent())]
switches = [("Airpump", airpump), ("Waterpump", waterpump), ("Heater", heater)]
val = rotary_knob.value()

devices = i2c.scan()
print("I2C Devices Found: ")
for device in devices:
        print("Device Address: 0x{:02X}".format(device))

oled.fill(1)
oled.show()
time.sleep(1)

val_old = rotary_knob.value()
but_old = rotary_button.value()
display_test('EncoderTest', 'Turn to Test', 'Push to Finish')
active=True
while active:
    val_new = rotary_knob.value()
    but_new = rotary_button.value()

    if but_old != but_new:
        but_old = but_new
        display_test('Camera Test', 'Capturing Image')
        time.sleep(1)
        cam.capture_jpg()
        display_test('Camera Test', 'Image Captured', 'Saving...')
        time.sleep_ms(2000)
        cam.saveJPG('image.jpg')
        time.sleep(1)
        display_test()
        active =False

    if val_old != val_new:
        val_old = val_new
        display_test('EncoderTest', 'Turn to Test', 'Push to Complete', f'step: {str(val_new)}')


try:
    while True:
        for switch in switches:
            switch[1].on()
            led.value(not led.value())
            display_test("Switch Test", switch[0], "LIGHT ON")
            time.sleep(2)
            switch[1].off()
        
        for sensor in sensors:
            led.value(not led.value())
            display_test("Sensor Test", sensor[0], sensor[1], 'Ctrl C to End')
            time.sleep(2)

except KeyboardInterrupt as e:
    print(e)
    led.off()
    display_test()
    if "testing" in os.listdir():
        os.remove("testing")
        print("Testing file deleted")
    if "image.jpg" in os.listdir():
        os.remove("image.jpg")
        print("Image file deleted")
   
    


