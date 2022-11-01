'''
Created on        24 October 2022
Last updated on   1 November 2022
@author:          Dappeschen
Installation      Data ORES elctrical energy meter with Qonnex 2Wire Belgium LOWI3- ref.: 3494546c709b
'''

import paho.mqtt.client as mqtt
import time
import datetime
from datetime import datetime
import pytz                         # for timezone()


def on_message(client, userdata, message):
    #Date and Tie in Central Europr / Brussels, Belgium
    dt_eur = datetime.now(pytz.timezone('Europe/Brussels'))
    #print MQTT received message's payload, predceeded by date/time stamp CET
    print(dt_eur.strftime("%Y:%m:%d %H:%M:%S %Z")," ", str(message.payload.decode("utf-8")))
    
#Preparing to connect to free MQTT test / broker server MOSQUITTO.org
mqttBroker ="test.mosquitto.org" 

client = mqtt.Client("LOWI-42")
client.connect(mqttBroker) 

client.loop_start()

client.subscribe("3494546c709b/PUB/CH0")
client.on_message=on_message 

time.sleep(300000) #wait 

print("done")

client.loop_stop()


