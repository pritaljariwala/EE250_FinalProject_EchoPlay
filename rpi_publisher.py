import time
import grovepi
import paho.mqtt.client as mqtt

SOUND_SENSOR = 14
grovepi.pinMode(SOUND_SENSOR, "INPUT")
rotary_sensor = 15
grovepi.pinMode(rotary_sensor, "INPUT")
BROKER_IP = "172.20.10.7"

value1 = grovepi.analogRead(SOUND_SENSOR)
client = mqtt.Client()
client.connect(BROKER_IP, 1883, 60)
cnt = 0
while True:
    try:
        if cnt == 5:
                value1 = grovepi.analogRead(SOUND_SENSOR)
                cnt = 0

        value2 = grovepi.analogRead(rotary_sensor)
        payload = str(value1) + "," + str(value2)
        client.publish("project/raw_sound", payload)
        time.sleep(0.2)      # 5 Hz publishing rate
        cnt = cnt +1

    except IOError:
        print("Sensor read error")
