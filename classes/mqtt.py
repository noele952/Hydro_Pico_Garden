from umqtt.simple import MQTTClient
import time
import ujson

class MQTT:
    def __init__(self, garden, mqtt_client,topic_pub, topic_sub=None):
        # Initialize MQTT object
        self.garden = garden
        self.topic_pub = topic_pub
        self.topic_sub = topic_sub
        self.mqtt_client = mqtt_client


    def post(self, label, data):
        # Publish data to MQTT broker
        try:
            message = ujson.dumps({ 'machine_id': self.garden.machine_id,
                                    'label' : 'data',
                                    'type' : label,
                                    'value': data })
            self.mqtt_client.publish(self.topic_pub, message)
        except Exception as error:
            print("An error occurred:", error)


    def mqtt_callback(self, topic, msg):
        # Handle incoming MQTT messages
        print("New message on topic {}".format(topic.decode('utf-8')))
        message = msg.decode('utf-8')
        print(message)
        if msg == "on":
            # Turn on the LED if the message is "on"
            print("on")
            garden.led.on()
        elif msg == "off":
            # Turn off the LED if the message is "off"
            print("off")
            garden.led.off()
        
     
