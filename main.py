import uasyncio as asyncio
import gc
gc.collect()
from microdot_asyncio import Microdot, Response
from routes import setup_routes
from classes.display import Display
from hydropico_machine.classes.mqtt import MQTT
from classes.menu_items import Wizard, Menu, Selection
from camera import Camera
from machine import SPI, Pin
from utime import sleep_ms
import utime
import os
import sys
import ubinascii
import ujson

display = Display(garden, I2C_channel=I2C_CHANNEL, I2C_clock=I2C_CLOCK, I2C_data=I2C_DATA, oled_height=OLED_HEIGHT, oled_width=OLED_WIDTH, rotary_btn_pin=R_BTN_PIN,
                 rotary_clock_pin=R_CL_PIN, rotary_data_pin=R_DT_PIN)


plant_select = Selection(display, 'CHOOSE PLANT', ['Scoll to Select', 'Press to Confirm'], [
                         'lettuce', 'tomato', 'basil'], 'plant_type')

garden_wiz = Wizard(display, [plant_select], lambda: print(display.menu_data.pop(
    'plant_type') if 'plant_type' in display.menu_data else print("Key not found")))

setup_menu = Menu(display, [('SETUP GARDEN', ['192.168.5.97', ':5000/']), ('CHOOSE PLANT', ['Push Knob', 'to select plant'], garden_wiz), ('TEMPERATURE', display.temperature), ('PRESSURE', display.pressure), ('HUMIDITY', display.humidity),
                ('PICO TEMP', display.internal_temp), ('WATER TEMP', display.thermistor_temp), ('', '')])

display.set_current(setup_menu)



app = Microdot()
Response.default_content_type = 'text/html'


cam = Camera(SPI(0,sck=Pin(18), miso=Pin(16), mosi=Pin(19)), Pin(17, Pin.OUT))


onboard_LED = Pin(25, Pin.OUT)
sleep_ms(1000)


setup_routes(app, garden)

reset_select = Selection(display, 'RESET GARDEN', [
                         'Would you like', 'to reset?'], ['YES', 'NO'], 'reset')

reset_wiz = Wizard(display, [reset_select], lambda: print(display.menu_data.pop(
    'reset', False) if 'reset' in display.menu_data else print("Key not found")))

main_menu = Menu(display, [('', ''), ('GARDEN INFO', display.garden_info), ('TEMPERATURE', display.temperature), ('PRESSURE', display.pressure), ('HUMIDITY', display.humidity),
            ('PICO TEMP', display.internal_temp), ('WATER TEMP', display.thermistor_temp), ('RESET', ['Press Button', 'To Reset', 'Garden'], reset_wiz), ('', '')])

display.set_current(main_menu)


async def monitor_rotary_knob(display):
    val_old = display.rotary_knob.value()
    but_old = display.rotary_button.value()
    while True:
        val_new = display.rotary_knob.value()
        but_new = display.rotary_button.value()
        if but_old != but_new:
            but_old = but_new
            print("button =", but_new)
            display.current.on_click()
        if val_old != val_new:
            if val_old < val_new:
                value=1
            elif val_new < val_old:
                value=-1
            val_old = val_new    
            print("step =", value)
            display.current.on_scroll(value)
        await asyncio.sleep(0.1)


async def mqtt_report(mqtt):
    while True:
        if garden.plant_type is None:
            await asyncio.sleep(3600)
        print("MQTT Reporting")
        try:
            mqtt.post('temperatureF', mqtt.garden.temp)
            mqtt.post('humidity', mqtt.garden.hum)
            mqtt.post('barometer', mqtt.garden.pres)
            mqtt.post('pico_tempF', mqtt.garden.temp_internal)
            mqtt.post('therm_tempF', mqtt.garden.temp_therm)
        except Exception as error:
            print("An error occured:", error)
        await asyncio.sleep(3600)


async def run_waterpump(garden):
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
    while True:
        garden.led.on()
        await asyncio.sleep(1)
        garden.led.off()
        await asyncio.sleep(1)
            

def encoded_file_generator(filename, chunk_size, finish_marker='END'):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            
            if not chunk:
                yield finish_marker
                break

            
            yield ubinascii.b2a_base64(chunk)


def gardenpic_filename():
    print(type(utime.time()))
    return 'garden_pic-' +str(utime.time())
           
 
def send_pic_mqtt(mqtt, filename, chunk_size=1536):
    gc.collect()
    pic_generator = encoded_file_generator(filename, chunk_size)
    chunk_counter = 0
    filename = gardenpic_filename()
    gc.collect()
    for piece in pic_generator:
        print('send as mqtt message')
        message = ujson.dumps({ 'machine_id': MACHINE_ID,
                                'label' : 'garden_pic',
                                'filename': filename,
                                'count' : chunk_counter,
                                'data': piece })
        print(message)
        try:
            mqtt.mqtt_client.publish(mqtt.topic_pub, message)
        except Exception as e:
            print(e)
        chunk_counter += 1
        utime.sleep(1)
    try:
        print("removing picture")
        os.remove('image.jpg')
    except Exception as e:
        print("pic removal failed")
        print(e)


async def take_garden_pic(mqtt, garden, cam):
    while True:
        if garden.plant_type is not None:
            gc.collect()
            onboard_LED.on()
            cam.capture_jpg()
            gc.collect()
            print("captured")
            sleep_ms(2000)
            cam.saveJPG('image.jpg')
            print("saved")
            onboard_LED.off()
            sleep_ms(2000)
            send_pic_mqtt(mqtt, 'image.jpg')
            await asyncio.sleep(3600)
        else:
            await asyncio.sleep(60)
    

async def microdot_server():
    await app.start_server(port=5000, debug=True)


async def main():
    while True:
        microdot_task = asyncio.create_task(microdot_server())
        waterpump_task = asyncio.create_task(run_waterpump(garden))
        airpump_task = asyncio.create_task(run_airpump(garden))
        mqtt_task = asyncio.create_task(mqtt_report(mqtt))
        # mqtt_listen_task = asyncio.create_task(mqtt_listen(mqtt))
        knob_task = asyncio.create_task(monitor_rotary_knob(display))
        camera_task = asyncio.create_task(take_garden_pic(mqtt, garden, cam))
        heartbeat_task = asyncio.create_task(heartbeat(garden))
        await asyncio.gather(microdot_task, waterpump_task, mqtt_task, airpump_task, knob_task, heartbeat_task)
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())