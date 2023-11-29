import ucryptolib
import json
import os

class ConfigManager:
    def __init__(self, filename, aes_cipher):
        # Initialize ConfigManager with specified filename
        self.filename = filename

        # Define hardware configuration constants
        self.aes_cipher = aes_cipher
        self. I2C_CLOCK = 7
        self.I2C_DATA = 6
        self.I2C_CHANNEL = 1
        self.APUMP_PIN = 22  
        self.WPUMP_PIN = 4
        self.PHOTORES_PIN = 27
        self.HEATER_PIN = 2
        self.LED_PIN = 15
        self.THERM_PIN = 26
        self.R_BTN_PIN = 12
        self.R_CL_PIN = 11
        self.R_DT_PIN = 10
        self.DEPTH_PIN = 3
        self.DEPTH_ADC = 28

        self.CAM_SCK = 18
        self.CAM_MISO = 16
        self.CAM_MOSI = 19
        self.CAM_CS = 17

        self.OLED_WIDTH = 128
        self.OLED_HEIGHT = 64

        # Define file paths and cryptographic constants
        self.AES_CIPHER = aes_cipher
        self.GARDEN_CONFIG_FILE = 'garden.json'
        self.MACHINE_ID = 'machine_id'
        self.CERT_FILE = '/certs/certificate.der'
        self.KEY_FILE = '/certs/private.der'
        self.PASSWORD_FILE = filename
        self.IMAGE_FILE = '/static/images/image.jpg'
        self.CLOUD_IMAGE_PREFIX = 'garden_pic'

        # AWS endpoint parameters.
        self.MQTT_CLIENT_ID="hydro_pico"
        # You can get tihs address from AWS IoT->Settings -> Endpoint
        self.MQTT_ENDPOINT='mqtt_endpoint'
        self.MQTT_CHUNK_SIZE=1536

        # Endpoint for Lambda function to retrieve most recent gardenpic
        self.LAMBDA_ENDPOINT_GARDENPIC='lambda_endpoint'

        # Load existing data or initialize an empty dictionary
        self.data = self.load_encrypted_data()  # Load existing data or initialize an empty dictionary

    def load_encrypted_data(self):
        try:
            with open(self.filename, 'rb') as file:
                # Read encrypted data from the file and decrypt
                encrypted_data = file.read()   
                return self.decrypt(encrypted_data)
        except OSError:
            # If file not found, create the file and return an empty dictionary
            print(f"File not found: {self.filename}")
            self.create_file()
            return {}
        except Exception as e:
            # Error loading data, return an empty dictionary
            print(f"Error loading data: {e}")
            return {}

    def create_file(self):
        try:
            with open(self.filename, 'wb') as file:
                # Write an empty encrypted data to create the file
                file.write(self.encrypt({}))
        except Exception as e:
            print(f"Error creating file: {e}")

    def save_to_config(self, value, *args):
        # Save a value to the configuration file
        current_level = self.data
        for arg in args[:-1]:
            current_level = current_level.setdefault(arg, {})
        current_level[args[-1]] = value
        self.update_config_file()

    def get_from_config(self, *args):
        # Retrieve a value from the configuration file
        current_level = self.data
        for arg in args[:-1]:
            current_level = current_level.get(arg, {})
            if not isinstance(current_level, dict):
                return None
        return current_level.get(args[-1])

    def remove_from_config(self, *args):
        # Remove a value from the configuration file
        current_level = self.data
        for arg in args[:-1]:
            current_level = current_level.get(arg, {})
            if not isinstance(current_level, dict):
                return
        current_level.pop(args[-1], None)
        self.update_config_file()

    def update_config_file(self):
        try:
            with open(self.filename, "wb") as file:
                # Save encrypted data to file
                file.write(self.encrypt(self.data))
        except Exception as e:
            print(f"Error saving data: {e}")

    def encrypt(self, data):
        # Encrypt data using AES cipher
        enc = ucryptolib.aes(self.AES_CIPHER, 1)
        data_bytes = json.dumps(data).encode()
        padding_len = 16 - (len(data_bytes) % 16)
        padded_data = data_bytes + bytes([padding_len] * padding_len)
        encrypted_data = enc.encrypt(padded_data)
        return encrypted_data

    def decrypt(self, encrypted_data):
        # Decrypt data using AES cipher
        dec = ucryptolib.aes(self.AES_CIPHER, 1)
        decrypted_data = dec.decrypt(encrypted_data)
        padding_len = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_len]
        decrypted_string = decrypted_data.decode()
        return json.loads(decrypted_string)