import network
import ssd1306
from classes.config import ConfigManager
from machine import I2C, Pin
from rotary_irq_pico import RotaryIRQ
from umqtt.simple import MQTTClient
import utime as time
import sys
import gc

# Display available memory before any allocations
print("Free Memory1:", gc.mem_free())

# List of characters for rotary entry and buttons 'back' and 'save'
my_data = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 ") + ['back', 'save']

# Load configuration from file
app_config = ConfigManager(filename='config.bin')
print(f'app_config.data: {app_config.data}')

# Initialize I2C for OLED display
i2c = I2C(app_config.I2C_CHANNEL, sda=Pin(app_config.I2C_DATA), scl=Pin(app_config.I2C_CLOCK))

# Initialize SSD1306 OLED display
oled = ssd1306.SSD1306_I2C(app_config.OLED_WIDTH,app_config.OLED_HEIGHT, i2c)


# Setup rotary encoder button and knob
rotary_button = Pin(app_config.R_BTN_PIN, Pin.IN, Pin.PULL_UP)
rotary_knob = RotaryIRQ(app_config.R_CL_PIN,
                        app_config.R_DT_PIN,
                        reverse=False, min_val=0,
                        max_val=len(my_data)-1,
                        incr=1,
                        range_mode=RotaryIRQ.RANGE_WRAP,
                        pull_up=True,
                        half_step=False)

# Display available memory after OLED and rotary setup
print("Free Memory2:", gc.mem_free())

# Connect to Wi-Fi
def do_connect(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        display_text("Connecting", "to network...")
        while not sta_if.isconnected():
            pass
    network_config =sta_if.ifconfig()
    app_config.save_to_config(network_config[0] + ':5000', 'wifi', 'webapp_address')
    print('Connected! Network config:', network_config)
    display_text("Connected!", "Network config:", str(network_config[0]))


# Log in to Wi-Fi
def login_wifi():
    ssid = app_config.get_from_config('wifi', 'credentials', 'ssid')
    password = app_config.get_from_config('wifi', 'credentials', 'password')
    
    if ssid and password:
        # Connect to Wi-Fi using ssid and password
        print("Connecting to Wi-Fi...")
        display_text("Connecting", "to WiFi")
        do_connect(ssid, password)
    else:
        # Display login screen and get credentials from the user
        print("Display login screen...")
#         ssid = input("Enter SSID: ")
#         password = input("Enter password: ")
        ssid = rotary_entry('SSID')
        password = rotary_entry('Password')
        # Save credentials and IP for future use
        print("Connecting to Wi-Fi...")
        display_text("Connecting", "to WiFi")
        time.sleep(1)
        do_connect(ssid, password)
        app_config.save_to_config(ssid, 'wifi', 'credentials', 'ssid')
        app_config.save_to_config(password, 'wifi', 'credentials', 'password')


# Display text on OLED
def display_text(line1='', line2='', line3='', line4=''):
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 16)
    oled.text(line3, 0, 32)
    oled.text(line4, 0, 48)
    oled.show()

# Function for rotary encoder input entry
def rotary_entry(value):
    display_text(f'Enter {value}', 'Turn to Select', 'Push to Confirm')
    entry = ''
    val_old = rotary_knob.value()
    but_old = rotary_button.value()
    active=True
    while active:
        val_new = rotary_knob.value()
        but_new = rotary_button.value()
       
        if but_old == 1 and but_new == 0:  # Check for falling edge (button press)
            print(f'Button Pressed: {but_new}')
            if my_data[val_new] == 'back':
                try:
                    entry = entry[:-1]
                except:
                    entry = ''
            elif my_data[val_new] == 'save':
                
                return entry
            else:    
                entry = entry + my_data[val_new]
            time.sleep(1)

        if val_old != val_new:
            val_old = val_new
            display_text(f'Enter {value}', 'Turn to Select', 'Push to Confirm', f'{entry}{my_data[val_new]}') 
        but_old = but_new
        time.sleep(0.1)
        
# Initial connection to Wi-Fi        
print("Connecting to your wifi...")
display_text("Connecting", "to your wifi...")
time.sleep(2)
login_wifi()       
gc.collect()
del my_data
del rotary_button
del rotary_knob

# Display available memory after Wi-Fi setup
print("Free Memory3:", gc.mem_free())

# Function for connecting to MQTT broker
def mqtt_connect(cert_file, key_file, endpoint, client_id):
    port = 8883
    keepalive = 3600
    max_retries = 3
    retry_count = 0
    with open(cert_file, 'rb') as f:
        cert = f.read()
        
    with open(key_file, 'rb') as f:
        key = f.read()

    print("Key and Certificate files Loaded")
    display_text("MQTT", "Key and", "Certificate", "files loaded")
    SSL_PARAMS = {'key': key, 'cert': cert, 'server_side': False}
    while retry_count < max_retries:
        try:
            client = MQTTClient(client_id, endpoint, port=port, keepalive=keepalive, ssl=True, ssl_params=SSL_PARAMS)
            client.connect()
            print('Connected to %s MQTT Broker' % (endpoint))
            display_text('', 'Connected to', 'MQTT Broker')
            return client
        except OSError as e:
            print(e)
            print('Failed to connect to the MQTT Broker. Retrying...')
            display_text('Failed to connect', 'to MQTT Broker', 'Retrying...')
            retry_count += 1
            time.sleep(5)

    print('Failed to connect to the MQTT Broker after multiple attempts.')
    display_text('Failed to connect', 'to MQTT Broker', f'after {max_retries} attempts')
    return None

# Connect to MQTT bro
mqtt_client = mqtt_connect(endpoint=app_config.MQTT_ENDPOINT,
                           client_id=app_config.MQTT_CLIENT_ID, 
                           cert_file=app_config.CERT_FILE,
                           key_file=app_config.KEY_FILE)
gc.collect()
time.sleep(2)
display_text()

print("Free Memory:", gc.mem_free())

# Importing modules and classes
import uasyncio as asyncio


gc.collect()

print("Free Memory5:", gc.mem_free())
del oled
del i2c

gc.collect()

print("Free Memory6:", gc.mem_free())
