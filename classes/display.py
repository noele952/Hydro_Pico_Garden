from machine import Pin, I2C
import ssd1306
from rotary_irq_pico import RotaryIRQ


class Display:
    def __init__(self, garden, I2C_channel, I2C_clock, I2C_data, oled_height, oled_width, rotary_btn_pin,
                 rotary_clock_pin, rotary_data_pin):
        # Initialize Display object with supplied parameters
        self.i2c = I2C(I2C_channel, sda=Pin(I2C_data), scl=Pin(I2C_clock))
        self.oled_width = oled_width
        self.oled_height = oled_height
        self.oled = ssd1306.SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
        self.rotary_button = Pin(rotary_btn_pin, Pin.IN, Pin.PULL_UP)
        self.rotary_knob = RotaryIRQ(
                                rotary_clock_pin,
                                rotary_data_pin,
                                reverse=False,
                                min_val=0,
                                max_val=9,
                                incr=1,
                                range_mode=RotaryIRQ.RANGE_WRAP,
                                pull_up=True,
                                half_step=False)    
        self.garden = garden
        self.stack = [] 
        self.current = None 
        self.menu_data = {} 
    

    def center(self, text, size):
        # Calculate offset for centering text based on size
        if text is None:
            return 0
        length = len(text)
        if size == 1:
            offset = ((self.oled_width - (8*length)) / 2)
        elif size == 2:
            offset = ((self.oled_height - (15*length)) / 2)
        else:
            return 0
        if offset < 0:
            return 0
        else:
            return int(offset)


    def display(self, content=None):
        # Display content on the OLED screen
        self.oled.fill(0)
        if content is not None:
            title = content[0]
            content = content[1]
            self.oled.write_text(title, self.center(title, 1), 0, 1)
        if isinstance(content, str) == True:
            self.oled.write_text(content, self.center(content, 2), 16, 2)
        elif isinstance(content, list) == True:
            line_count = len(content)
            if line_count >= 2:
                self.oled.write_text(content[0], self.center(content[0], 1), 16, 1)
                self.oled.write_text(content[1], self.center(content[1], 1), 32, 1)
            if line_count > 2:
                self.oled.write_text(content[2], self.center(content[2], 1), 46, 1)
            if line_count == 4:
                self.oled.write_text(content[3], self.center(content[3], 1), 56, 1)
        else:
            pass
        self.oled.show()
    
    def set_current(self, obj):
        # Set the current control object and execute its on_current method
        # always do this when we change the control object
        self.stack.append(obj)
        self.current = obj
        self.current.on_current()
    
    
    def back(self):
        # Navigate back in the menu stack
        if len(self.stack) > 1:
            self.stack.pop()    
        self.set_current(self.stack.pop())
    
    def temperature(self):
        # Get temperature information from the garden object
        temperature_cf = self.garden.temperature()
        return temperature_cf[1][:-3] + ' F'
        
    def pressure(self):
        # Get pressure information from the garden object
        return self.garden.pressure().split('.')[0] + ' hPa'
                                 
    def humidity(self):
        # Get humidity information from the garden object
        return self.garden.humidity()
    
    def internal_temp(self):
        # Get internal temperature information from the garden object
        temperature_cf = self.garden.internal_temp()
        return temperature_cf[1]
    
    def thermistor_temp(self):
        # Get thermistor temperature information from the garden object
        temperature_cf = self.garden.thermistor_temp()
        return temperature_cf[1][:-3] + ' F'
    
    def garden_info(self):
        # Get information about the garden (plant type and days planted)
        plant_type = self.garden.plant_type
        days_planted = str(self.garden.days_planted())
        if plant_type is None:
            return ['', 'Days Planted:', days_planted]
        return [f'{plant_type[0].upper() + plant_type[1:]}', 'Days Planted:', days_planted]

    def webapp_address(self):
        # Return the web app address for display
        return "192.168.5.97:5000"
   