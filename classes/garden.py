from machine import ADC, Pin, I2C, reset
import bme280
import math
import time
import json
from data.garden_data import plant_data


class Garden:
    def __init__(self, plant_type, config_file, machine_id, waterpump_pin, airpump_pin, thermistor_pin, led_pin, I2C_channel, I2C_clock, I2C_data):
        self.machine_id = machine_id
        self.thermistor = ADC(thermistor_pin)
        self.internal_temp_sensor = ADC(4)            
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
        return float(''.join(char for char in self.temperature()[1] if not (
    char.isalpha() or char.isspace())))
         
    
    @property
    def hum(self):
        return float(self.humidity().replace(" ", "").replace("%", "").strip())
    
    @property
    def pres(self):
        return float(''.join(char for char in self.pressure() if not (
    char.isalpha() or char.isspace())))
        
    
    @property
    def temp_internal(self):
        return float(''.join(char for char in self.internal_temp()[1] if not (
    char.isalpha() or char.isspace())))
    
    
    @property
    def temp_therm(self):
        return float(''.join(char for char in self.thermistor_temp()[1] if not (
    char.isalpha() or char.isspace())))

    
    @property
    def days(self):
        
        return self.days_planted()
    
    @property
    def airpump_status(self):
        return self.is_pin_on(self.airpump)
    
    @property
    def waterpump_status(self):
        return self.is_pin_on(self.waterpump)
        
    def is_pin_on(self, component):
        return component.value()
    
        
    def config_file_exists(self, config_file):  # no os.path in MicroPython, workaround
        try:
            with open(config_file, 'r'):
                return True
        except OSError:
            return False    
        
        
    def save_config(self):
        config_data = {
            "plant_type": self.plant_type,
            "start_time": time.time()
            
        }
        if self.plant_type is not None:
            self.data = plant_data[self.plant_type]
        with open(self.config_file, 'w') as file:
            json.dump(config_data, file)
        
    def load_from_config(self):
        try:
            with open(self.config_file, 'r') as file:
                config_data = json.load(file)
                self.plant_type = config_data.get("plant_type")
                self.start_time = config_data.get("start_time")
                self.data = plant_data[self.plant_type]
        except Exception as e:
            print(f"Error loading config file: {e}")
        
        
    def time_planted(self):
        return time.time() - self.start_time
    
    
    def days_planted(self):
        try:
            days = math.floor(self.time_planted() / (60*60*24))
            return days
        except:
            return 0
    
        
    def internal_temp(self):
        adc_value = self.internal_temp_sensor.read_u16()
        volt = (3.3/65535) * adc_value
        temp = round((27 - (volt - 0.706)/0.001721), 1)
        temp_c = str(temp) + ' C'
        temp_f = str(round(((temp * (9/5)) + 32), 1)) + ' F'
        return (temp_c, temp_f)
        
        
    def temperature(self):    
        temp_c = self.bme.temperature[:-2] + ' C'
        temp_f = str((float(temp_c[:-2]) * 9/5) + 32) + ' F'
        return (temp_c, temp_f)
        
        
    def humidity(self):    
        hum = self.bme.humidity.split('.')[0] + ' %'
        return hum
        
        
    def pressure(self):    
        pres = self.bme.pressure[:-3] + ' hPa'
        return pres
        
        
    def thermistor_temp(self):
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
        
        
    def reset(self):
        config_data = {
            "plant_type": None
        }
        with open(self.config_file, 'w') as file:
            json.dump(config_data, file)
        self.start_time = None
        self.plant_type = None
        self.data = None
        self.airpump.off()
        self.waterpump.off()
        self.led.off()
        reset()
