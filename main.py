from microdot_asyncio import Microdot, Response
from routes import setup_routes
from classes.menu_items import Wizard, Menu, Selection
from classes.display import Display
from classes.mqtt import MQTT
from classes.garden import Garden
from camera import Camera
from machine import SPI, Pin
from machine import WDT
from utime import sleep, sleep_ms
import os
import ubinascii
import ujson



garden = Garden(plant_type=None, config_file=app_config.GARDEN_CONFIG_FILE, machine_id=app_config.MACHINE_ID,
                waterpump_pin=app_config.WPUMP_PIN, airpump_pin=app_config.APUMP_PIN, thermistor_pin=app_config.THERM_PIN,
                heater_pin=app_config.HEATER_PIN, photoresistor_pin=app_config.PHOTORES_PIN ,led_pin=app_config.LED_PIN,
                I2C_channel=app_config.I2C_CHANNEL, I2C_clock=app_config.I2C_CLOCK,
                I2C_data=app_config.I2C_DATA)

gc.collect()
print("Free Memory7:", gc.mem_free())

# Create an instance of the Display class
display = Display(garden, I2C_channel=app_config.I2C_CHANNEL, I2C_clock=app_config.I2C_CLOCK, I2C_data=app_config.I2C_DATA,
                  oled_height=app_config.OLED_HEIGHT, oled_width=app_config.OLED_WIDTH, rotary_btn_pin=app_config.R_BTN_PIN,
                 rotary_clock_pin=app_config.R_CL_PIN, rotary_data_pin=app_config.R_DT_PIN)

# Intiate items for OLED screen menu
plant_select = Selection(display, 'CHOOSE PLANT', ['Scoll to Select', 'Press to Confirm'], [
                         'lettuce', 'tomato', 'basil'], 'plant_type')

garden_wiz = Wizard(display, [plant_select], lambda: print(display.menu_data.pop(
    'plant_type') if 'plant_type' in display.menu_data else print("Key not found")))

# setup_menu = Menu(display, [('SETUP GARDEN', ['192.168.5.97', ':5000/']), ('CHOOSE PLANT', ['Push Knob', 'to select plant'], garden_wiz), ('TEMPERATURE', display.temperature), ('PRESSURE', display.pressure), ('HUMIDITY', display.humidity),
#                 ('PICO TEMP', display.internal_temp), ('WATER TEMP', display.thermistor_temp), ('', '')])
# 
# display.set_current(setup_menu)




# Creating an instance of the MQTT class for communication with the MQTT broker
mqtt = MQTT(garden, mqtt_client, topic_pub=b'GardenData')

# Creating an instance of the Microdot web server
app = Microdot()
Response.default_content_type = 'text/html'

# Initialize the camera
cam = Camera(SPI(0,sck=Pin(app_config.CAM_SCK), miso=Pin(app_config.CAM_MISO), mosi=Pin(app_config.CAM_MOSI)), Pin(app_config.CAM_CS, Pin.OUT))

# Initializing onboard LED pin
onboard_LED = Pin(25, Pin.OUT) #Fixed Internal Pin Number
sleep_ms(1000)

# Setting up routes for the Microdot web server
setup_routes(app, garden)

# Creating a selection menu for resetting the
reset_select = Selection(display, 'RESET GARDEN', [
                         'Would you like', 'to reset?'], ['YES', 'NO'], 'reset')

# Creating a wizard for handling the reset selection
reset_wiz = Wizard(display, [reset_select], lambda: print(display.menu_data.pop(
    'reset', False) if 'reset' in display.menu_data else print("Key not found")))

# Creating the main menu for display
main_menu = Menu(display, [('', ''), ('SETUP GARDEN', ['192.168.5.97', ':5000/']), ('GARDEN INFO', display.garden_info),('CHOOSE PLANT', ['Push Knob', 'to select plant'], garden_wiz), ('TEMPERATURE', display.temperature), ('BAROMETER', display.pressure), ('HUMIDITY', display.humidity),
            ('CPU TEMP', display.internal_temp), ('WATER TEMP', display.thermistor_temp), ('RESET', ['Press Button', 'To Reset', 'Garden'], reset_wiz), ('', '')])

# Setting the main menu as the initial display
display.set_current(main_menu)


# Asynchronous tasks

async def monitor_rotary_knob(display):
    # Monitor rotary knob and button
    val_old = display.rotary_knob.value()
    but_old = display.rotary_button.value()
    while True:
        val_new = display.rotary_knob.value()
        but_new = display.rotary_button.value()
        if but_old != but_new:
            # Button press detected
            but_old = but_new
            print("button =", but_new)
            display.current.on_click()
        if val_old != val_new:
            # Rotary knob rotation detected
            if val_old < val_new:
                value=1
            elif val_new < val_old:
                value=-1
            val_old = val_new    
            print("step =", value)
            display.current.on_scroll(value)
        await asyncio.sleep(0.1)


async def mqtt_report(mqtt):
    # Periodically report sensor data to MQTT broker
    while True:
        if garden.plant_type is None:
            await asyncio.sleep(3600) # Sleep for an hour if no plant is selected
        print("MQTT Reporting")
        try:
            # Post sensor data to MQTT topics
            mqtt.post('temperatureF', mqtt.garden.temp)
            mqtt.post('humidity', mqtt.garden.hum)
            mqtt.post('barometer', mqtt.garden.pres)
            mqtt.post('pico_tempF', mqtt.garden.temp_internal)
            mqtt.post('therm_tempF', mqtt.garden.temp_therm)
            mqtt.post('photo_resistor', mqtt.garden.photoresistor_percent())
        except Exception as error:
            print("An mqtt post error occured:", error)
        await asyncio.sleep(3600) # Sleep for an hour


async def run_waterpump(garden):
    # Run water pump based on garden configuration
    while True:
        if garden.plant_type is not None:
            garden.waterpump.on()
            garden.led.on()
            duration = garden.data['waterpump_duration']
            interval = garden.data['waterpump_interval']
            print("Water Pump ON")
            await asyncio.sleep(duration)
            garden.waterpump.off()
            garden.led.off()
            print("Water Pump OFF")
            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(10)


async def run_airpump(garden):
    # Run air pump based on garden configuration
    while True:
        if garden.plant_type is not None:
            duration = garden.data['airpump_duration']
            interval = garden.data['airpump_interval']
            garden.airpump.on()
            print("Air Pump ON")
            await asyncio.sleep(duration) 
            garden.airpump.off()
            print("Air Pump OFF")
            await asyncio.sleep(interval) 
        else:
            await asyncio.sleep(10)
            
            
async def heartbeat(garden):
    # Toggle the attached LED as a heartbeat indicator
    while True:
        garden.led.on()
        await asyncio.sleep(1)
        garden.led.off()
        await asyncio.sleep(1)
            
            
def encoded_file_generator(filename, chunk_size, finish_marker='END'):
    # Generator function to encode a file in chunks and yield as base64
    print("encoded_file_generator")
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            
            if not chunk:
                # Reached end of file, yield finish marker
                yield finish_marker
                break
            
            yield ubinascii.b2a_base64(chunk)


def gardenpic_filename():
    # Generate a filename for the garden picture
    return f'{app_config.CLOUD_IMAGE_PREFIX}-time'
           
 
def send_pic_mqtt(mqtt, filename, chunk_size=app_config.MQTT_CHUNK_SIZE):
    # Send garden picture to MQTT in chunks
    gc.collect()
    print("in send_pic_mqtt")
    pic_generator = encoded_file_generator(filename, chunk_size)
    # image_generator = cam.generate_image_chunks()
    print(pic_generator)
    print(type(pic_generator))
    chunk_counter = 0
    filename = gardenpic_filename()
    print(filename)
    gc.collect()
    for piece in pic_generator:
        print('send as mqtt message')
        gc.collect()
        print("Free MemoryGEN:", gc.mem_free())
        message = ujson.dumps({ 'machine_id': app_config.MACHINE_ID,
                                'label' : app_config.CLOUD_IMAGE_PREFIX,
                                'filename': filename,
                                'count' : chunk_counter,
                                'data': piece })
        gc.collect()
        print("Free MemoryGEN:", gc.mem_free())
        try:
            mqtt.mqtt_client.publish(mqtt.topic_pub, message)
            print(message)
        except Exception as e:
            print(e)
        chunk_counter += 1
        time.sleep(1)
    

async def take_garden_pic(mqtt, garden, cam):
    # Capture and send garden picture periodically
    while True:
        await asyncio.sleep(20)
        try:
            print("removing picture")
            os.remove(app_config.IMAGE_FILE)
        except Exception as e:
            print("pic removal failed")
            print(e)    
        if garden.plant_type is not None:
            gc.collect()
            print("Free Memory7:", gc.mem_free())
            onboard_LED.on()
            cam.capture_jpg()
            gc.collect()
            print("Free Memory8:", gc.mem_free())
            print("captured")
            sleep_ms(2000)
            #cam.saveJPG(app_config.IMAGE_FILE)
            print("saved")
            onboard_LED.off()
            gc.collect()
            chunk_counter = 0
            print("Free Memory9:", gc.mem_free())
            for jpg_chunk_hex in cam.generateJPG(1024):
                #print(f'binary: {jpg_chunk_hex}')
                jpeg_chunk_base64 = ubinascii.b2a_base64(jpg_chunk_hex)
                #print(f'base64: {jpeg_chunk_base64}')
                message = ujson.dumps({ 'machine_id': app_config.MACHINE_ID,
                                'label' : app_config.CLOUD_IMAGE_PREFIX,
                                'filename': 'test',
                                'count' : chunk_counter,
                                'data': jpeg_chunk_base64})
                chunk_counter += 1
                gc.collect()
                print("Free MemoryGEN:", gc.mem_free())
                try:
                    mqtt.mqtt_client.publish(mqtt.topic_pub, message)
                    print(message)
                except Exception as e:
                    print(e)
                await asyncio.sleep(.1)
            #send_pic_mqtt(mqtt, app_config.IMAGE_FILE)
            await asyncio.sleep(3600)
        else:
            await asyncio.sleep(60)


async def heater_control(garden):
    # Control the garden heater based on temperature settings
    garden.heater.duty_u16(0)
    target_temp = 68 #config.garden.temp
    wdt = WDT(timeout=8000)  #watchdog timer set for 8 seconds
    while True:
        wdt.feed() #watchdog timer reloads
        desired_temp = int(garden.data['water_temp'])
        print(f'desired_temp: {desired_temp}')
        current_temp = float(garden.thermistor_temp()[1][:-2])
        print(f'current_temp: {current_temp}') 
        temp_dif = current_temp - desired_temp
        if temp_dif < 0:
            garden.heater.duty_u16(32768) #  duty cycle = duty_u16/65535
        else:
            garden.heater.duty_u16(0)
        wdt.feed()    
        await asyncio.sleep(3)    
        

async def microdot_server():
    # Start the Microdot web server
    await app.start_server(port=5000, debug=True)
    

async def main():
    # Main loop to run all asynchronous tasks
    while True:
        microdot_task = asyncio.create_task(microdot_server())
        waterpump_task = asyncio.create_task(run_waterpump(garden))
        airpump_task = asyncio.create_task(run_airpump(garden))
        mqtt_task = asyncio.create_task(mqtt_report(mqtt))
        knob_task = asyncio.create_task(monitor_rotary_knob(display))
        camera_task = asyncio.create_task(take_garden_pic(mqtt, garden, cam))
        heater_task = asyncio.create_task(heater_control(garden))
        heartbeat_task = asyncio.create_task(heartbeat(garden))
        await asyncio.gather(microdot_task, waterpump_task, mqtt_task, airpump_task, knob_task, heartbeat_task, heater_task)
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())