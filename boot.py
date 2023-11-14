import network
from classes.config import ConfigManager
from classes.display import Display
from classes.mqtt import MQTT
from classes.garden import Garden
from classes.menu_items import Menu, Wizard, Selection


I2C_CLOCK = 7
I2C_DATA = 6
I2C_CHANNEL = 1
APUMP_PIN = 22  
WPUMP_PIN = 27  
HEATER_PIN = 28
LED_PIN = 15
THERM_PIN = 26
OLED_WIDTH = 128
OLED_HEIGHT = 64
R_BTN_PIN = 12
R_CL_PIN = 11
R_DT_PIN = 10

AES_CIPHER = b'1234567890123456'
GARDEN_CONFIG_FILE = 'garden.json'
MACHINE_ID = 'machine_id'
CERT_FILE = '/certs/certificate.der'
KEY_FILE = '/certs/private.der'


wifi_cred = ConfigManager(filename='config.bin', aes_cipher=AES_CIPHER)


def do_connect(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    network_config =sta_if.ifconfig()
    wifi_cred.save_to_config(network_config[0] + ':5000', 'wifi', 'webapp_address')
    print('Connected! Network config:', network_config)


def login_wifi():
    ssid = wifi_cred.get_from_config('wifi', 'credentials', 'ssid')
    password = wifi_cred.get_from_config('wifi', 'credentials', 'password')
    if ssid and password:
        # Connect to Wi-Fi using ssid and password
        print("Connecting to Wi-Fi...")
        do_connect(ssid, password)
    else:
        # Display login screen and get credentials from the user
        print("Display login screen...")
        ssid = input("Enter SSID: ")
        password = input("Enter password: ")
        # Save credentials and IP for future use
        wifi_cred.save_to_config(ssid, 'wifi', 'credentials', 'ssid')
        wifi_cred.save_to_config(password, 'wifi', 'credentials', 'password')
        print("Connecting to Wi-Fi...")
        do_connect(ssid, password)

    
print("Connecting to your wifi...")
login_wifi()

# AWS endpoint parameters.
# Should be different for each device can be anything
CLIENT_ID="hydro_pico"
# You can get tihs address from AWS IoT->Settings -> Endpoint
# mothing like : {host id}.iot.{region}.amazonaws.com
MQTT_ENDPOINT='mqtt_endpoint'
garden = Garden(plant_type=None, config_file=GARDEN_CONFIG_FILE, machine_id=MACHINE_ID, waterpump_pin=WPUMP_PIN, airpump_pin=APUMP_PIN,
                thermistor_pin=THERM_PIN, led_pin=LED_PIN, I2C_channel=I2C_CHANNEL, I2C_clock=I2C_CLOCK, I2C_data=I2C_DATA)

mqtt = MQTT(garden, endpoint=MQTT_ENDPOINT, client_id=CLIENT_ID, topic_pub=b'GardenData',
            cert_file=CERT_FILE, key_file=KEY_FILE)
