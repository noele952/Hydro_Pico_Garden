from machine import ADC, Pin, I2C, reset, PWM
import bme280
import math
import time
import json
from data.garden_data import plant_data


class Garden:
    def __init__(self, plant_type, config_file, machine_id, waterpump_pin, airpump_pin, heater_pin, thermistor_pin, photoresistor_pin, led_pin, I2C_channel, I2C_clock, I2C_data):
        """
        Initialize the Garden class.

        Parameters:
        - plant_type: Type of plant in the garden
        - config_file: File path for configuration storage
        - machine_id: Unique identifier for the garden machine
        - waterpump_pin: GPIO pin for the water pump.
        - airpump_pin: GPIO pin for the air pump
        - heater_pin: GPIO pin for the heater
        - thermistor_pin: GPIO pin for the thermistor
        - photoresistor_pin: GPIO pin for the photoresistor
        - led_pin: GPIO pin for the LED
        - I2C_channel: I2C communication channel
        - I2C_clock: GPIO pin for I2C clock.
        - I2C_data: GPIO pin for I2C data.

        Attributes:
        - machine_id: Unique identifier for the garden machine
        - thermistor: ADC object for reading temperature from the thermistor
        - heater: PWM object for controlling the heater
        - internal_temp_sensor: ADC object for reading internal temperature
        - photoresistor: ADC object for reading light intensity from the photoresistor
        - airpump: Pin object for controlling the air pump
        - waterpump: Pin object for controlling the water pump
        - led: Pin object for controlling the LED
        - i2c: I2C protovol object
        - bme: BME280 object for reading temperature, pressure, and humidity
        - plant_type: Type of plant in the garden
        - start_time: Time when the garden was started (Unix time)
        - config_file: File path for configuration storage.
        - data: Data container for garden information.
        """
        
        self.machine_id = machine_id
        self.thermistor = ADC(thermistor_pin)
        self.heater = PWM(Pin(heater_pin))
        self.heater.freq(60)
        self.heater.duty_u16(0)# duty_u16 sets the duty cycle as a ratio duty_u16 / 65535
        self.internal_temp_sensor = ADC(4)
        self.photoresistor = ADC(photoresistor_pin)
        self.airpump = Pin(airpump_pin, Pin.OUT)
        self.waterpump = Pin(waterpump_pin, Pin.OUT)
        self.led = Pin(led_pin, Pin.OUT)
        self.i2c = I2C(I2C_channel, sda=Pin(I2C_data), scl=Pin(I2C_clock))
        self.bme = bme280.BME280(i2c=self.i2c)
        self.plant_type = plant_type
        self.start_time = time.time()
        self.config_file = config_file
        self.data = None
        if self.config_file_exists(config_file):
            self.load_from_config()
        else:
            self.save_config()
        
    @property
    def temp(self):
        # Return float temperature F, change self.temperature()[1] to [0] for C
        return float(''.join(char for char in self.temperature()[1] if not (
    char.isalpha() or char.isspace())))
         
    
    @property
    def hum(self):
        # Return float humidity percentage
        return float(self.humidity().replace(" ", "").replace("%", "").strip())
    
    @property
    def pres(self):
        # Return float barometric pressure in hPa
        return float(''.join(char for char in self.pressure() if not (
    char.isalpha() or char.isspace())))
        
    
    @property
    def temp_internal(self):
        # Return float Pico internal Temp F, change self.internal_temp()[1] to [0] for C
        return float(''.join(char for char in self.internal_temp()[1] if not (
    char.isalpha() or char.isspace())))
    
    
    @property
    def temp_therm(self):
        # Return float water temperature  F, change self.thermistor_temp()[1] to [0] for C
        return float(''.join(char for char in self.thermistor_temp()[1] if not (
    char.isalpha() or char.isspace())))

    
    @property
    def days(self):
        # Return int days planted
        return self.days_planted()
    
    @property
    def airpump_status(self):
        # Return int waterpump status 0/1 - OFF/ON
        return self.is_pin_on(self.airpump)
    
    @property
    def waterpump_status(self):
        # Return int waterpump status 0/1 - OFF/ON
        return self.is_pin_on(self.waterpump)
        
    def is_pin_on(self, component):
        # Return int pin value 0/1
        return component.value()
    
        
    def config_file_exists(self, config_file):  # no os.path in MicroPython, workaround
        # Return bool, config file exists?
        try:
            with open(config_file, 'r'):
                return True
        except OSError:
            return False    
        
        
    def save_config(self):
        # Save configuration data file
        config_data = {
            "plant_type": self.plant_type,
            "start_time": time.time()
            
        }
        if self.plant_type is not None:
            self.data = plant_data[self.plant_type]
        with open(self.config_file, 'w') as file:
            json.dump(config_data, file)
        
    def load_from_config(self):
        # Load configuration file
        try:
            with open(self.config_file, 'r') as file:
                config_data = json.load(file)
                self.plant_type = config_data.get("plant_type")
                self.start_time = config_data.get("start_time")
                self.data = plant_data[self.plant_type]
        except Exception as e:
            print(f"Error loading config file: {e}")
        
        
    def time_planted(self):
        # Return float Unix time
        return time.time() - self.start_time
    
    
    def days_planted(self):
        # Return int days planted, 0 if no garden planted
        try:
            days = math.floor(self.time_planted() / (60*60*24))
            return days
        except:
            return 0
    
        
    def internal_temp(self):
        # Return str Pico internal temp as a tuple ('{temp_c} C', '{temp_f} F')
        adc_value = self.internal_temp_sensor.read_u16()
        volt = (3.3/65535) * adc_value
        temp = round((27 - (volt - 0.706)/0.001721), 1)
        temp_c = str(temp) + ' C'
        temp_f = str(round(((temp * (9/5)) + 32), 1)) + ' F'
        return (temp_c, temp_f)
        
        
    def temperature(self):
        # Return str Ptemp as a tuple ('{temp_c} C', '{temp_f} F')
        temp_c = self.bme.temperature[:-2] + ' C'
        temp_f = str((float(temp_c[:-2]) * 9/5) + 32) + ' F'
        return (temp_c, temp_f)
        
        
    def humidity(self):
        # Return str humidity '{hum} %'
        hum = self.bme.humidity.split('.')[0] + ' %'
        return hum
        
        
    def pressure(self):
        # Return str barometric pressure '{hpres} hPa'
        pres = self.bme.pressure[:-3] + ' hPa'
        return pres
        
        
    def thermistor_temp(self):
        # Return str temperature in Celsius, '{temp} C'
        adc = self.thermistor.read_u16()
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
        temp_f = f'{(round(temp_k - 273.15, 1) * (9/5)) + 32} F'
        
        return (temp_c, temp_f)
        
    def photoresistor_percent(self):
        # Calculate the light level returned as a percentage based of ADC value 0-65535
        photo_value = self.photoresistor.read_u16()
        light_percentage = str(round(photo_value/65535*100, 2))
        return light_percentage
        
    
    def reset(self):
        # Reset the garden by removing current configuration, turning off pumps, and restarting machine
        # Note: will not reset Pico when attached to USB power; stops but does not reboot
        
        # Reset configuration data
        config_data = {
            "plant_type": None
        }
        with open(self.config_file, 'w') as file:
            json.dump(config_data, file)   
        self.start_time = None
        self.plant_type = None
        self.data = None
        
        # Turn off pumps and LED
        self.airpump.off()
        self.waterpump.off()
        self.led.off()
        
        # Restart the system
        reset()
