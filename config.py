import ucryptolib
import json
import os

class ConfigManager:
    def __init__(self, filename, aes_cipher):
        self.filename = filename
        self.aes_cipher = aes_cipher
        self. I2C_CLOCK = 7
        self.I2C_DATA = 6
        self.I2C_CHANNEL = 1
        self.APUMP_PIN = 22  
        self.WPUMP_PIN = 4
        self.PHOTORES_PIN = 27
        self.HEATER_PIN = 28
        self.LED_PIN = 15
        self.THERM_PIN = 26
        self.R_BTN_PIN = 12
        self.R_CL_PIN = 11
        self.R_DT_PIN = 10

        self.CAM_SCK = 18
        self.CAM_MISO = 16
        self.CAM_MOSI = 19
        self.CAM_CS = 17

        self.OLED_WIDTH = 128
        self.OLED_HEIGHT = 64

        self.AES_CIPHER = aes_cipher
        self.GARDEN_CONFIG_FILE = 'garden.json'
        self.MACHINE_ID = 'machine_id'
        self.CERT_FILE = '/certs/certificate.der'
        self.KEY_FILE = '/certs/private.der'
        self.PASSWORD_FILE = filename
        self.IMAGE_FILE = '/static/images/image.jpg'
        self.CLOUD_IMAGE_PREFIX = 'garden_pic'
        # AWS endpoint parameters.
        # Should be different for each device can be anything
        self.MQTT_CLIENT_ID="hydro_pico"
        # You can get tihs address from AWS IoT->Settings -> Endpoint
        # something like : {host id}.iot.{region}.amazonaws.com
        self.MQTT_ENDPOINT='mqtt_endpoint'
        self.MQTT_CHUNK_SIZE=1536
        self.data = self.load_encrypted_data()  # Load existing data or initialize an empty dictionary

    def load_encrypted_data(self):
        try:
            with open(self.filename, 'rb') as file:
                encrypted_data = file.read()   
                return self.decrypt(encrypted_data)
        except OSError:
            print(f"File not found: {self.filename}")
            self.create_file()  # Create the file if it doesn't exist
            return {}
        except Exception as e:
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
        current_level = self.data
        for arg in args[:-1]:
            current_level = current_level.setdefault(arg, {})
        current_level[args[-1]] = value
        self.update_config_file()

    def get_from_config(self, *args):
        current_level = self.data
        for arg in args[:-1]:
            current_level = current_level.get(arg, {})
            if not isinstance(current_level, dict):
                return None
        return current_level.get(args[-1])

    def remove_from_config(self, *args):
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
                # Save encrypted data
                file.write(self.encrypt(self.data))
        except Exception as e:
            print(f"Error saving data: {e}")

    def encrypt(self, data):
        enc = ucryptolib.aes(self.aes_cipher, 1)
        data_bytes = json.dumps(data).encode()
        padding_len = 16 - (len(data_bytes) % 16)
        padded_data = data_bytes + bytes([padding_len] * padding_len)
        encrypted_data = enc.encrypt(padded_data)
        return encrypted_data

    def decrypt(self, encrypted_data):
        dec = ucryptolib.aes(self.aes_cipher, 1)
        decrypted_data = dec.decrypt(encrypted_data)
        padding_len = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_len]
        decrypted_string = decrypted_data.decode()
        return json.loads(decrypted_string)

