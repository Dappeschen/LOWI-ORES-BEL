'''
Created on 24 oct. 2022

@author: Dappeschen
'''

import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

mqttBroker ="test.mosquitto.org" 

client = mqtt.Client("LOWI-42")
client.connect(mqttBroker) 

client.loop_start()

client.subscribe("<put your LOWI's 12 digit MAC address here>/PUB/CH0")
client.on_message=on_message 

time.sleep(300000) #wait 

print("done")

client.loop_stop()


