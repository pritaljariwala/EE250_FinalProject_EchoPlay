# rpi_publisher.py
import time
import grovepi
import paho.mqtt.client as mqtt

SOUND_SENSOR = 0
VOLUME_SENSOR = 2 
grovepi.pinMode(SOUND_SENSOR, "INPUT")
grovepi.pinMode(VOLUME_SENSOR, "INPUT")


BROKER_IP = "172.20.10.6"   # replace with YOUR laptop's or Pi's broker

client = mqtt.Client()
client.connect(BROKER_IP, 1883, 60)

while True:
    try:
        value = grovepi.analogRead(SOUND_SENSOR)
        client.publish("project/raw_sound", value)
        time.sleep(0.005)      # 200 Hz publishing rate

    except IOError:
        print("Sensor read error")
