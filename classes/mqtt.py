from umqtt.simple import MQTTClient
import time
import ujson


class MQTT:
    def __init__(self, garden, endpoint, client_id, topic_pub, cert_file, key_file, topic_sub=None):
        self.garden = garden
        self.endpoint = endpoint
        self.client_id = client_id
        self.topic_pub = topic_pub
        self.topic_sub = topic_sub
        self.cert_file = cert_file
        self.key_file = key_file
        self.port = 8883
        self.keepalive = 3600
        self.max_retries = 3
        self.retry_count = 0
        self.mqtt_client = self.connect()


    def connect(self):
        with open(self.cert_file, 'rb') as f:
            cert = f.read()
            
        with open(self.key_file, 'rb') as f:
            key = f.read()

        print("Key and Certificate files Loaded")

        SSL_PARAMS = {'key': key, 'cert': cert, 'server_side': False}
        while self.retry_count < self.max_retries:
            try:
                client = MQTTClient(self.client_id, self.endpoint, port=self.port, keepalive=self.keepalive, ssl=True, ssl_params=SSL_PARAMS)
                client.connect()
                print('Connected to %s MQTT Broker' % (self.endpoint))
                return client
            except OSError as e:
                print(e)
                print('Failed to connect to the MQTT Broker. Retrying...')
                self.retry_count += 1
                time.sleep(5)

        print('Failed to connect to the MQTT Broker after multiple attempts.')
        return None


    def post(self, label, data):
        try:
            message = ujson.dumps({ 'machine_id': self.garden.machine_id,
                                    'label' : 'data',
                                    'type' : label,
                                    'value': data })
            self.mqtt_client.publish(self.topic_pub, message)
        except Exception as error:
            print("An error occurred:", error)


    def mqtt_callback(self, topic, msg):
        print("New message on topic {}".format(topic.decode('utf-8')))
        message = msg.decode('utf-8')
        print(message)
        if msg == "on":
            print("on")
            garden.led.on()
        elif msg == "off":
            print("off")
            garden.led.off()
        
