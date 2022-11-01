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
import json
 

def on_message(client, userdata, message):
    #Date and Tie in Central Europr / Brussels, Belgium
    dt_eur = datetime.now(pytz.timezone('Europe/Brussels'))
    
    #prepare to print MQTT received message's payload, preceeded by date/time stamp - in Central Europe Time (CET) time zone 
    json_string = str(message.payload.decode("utf-8"))
    
    #claculate length / number of characters of message's payload
    payload_length = len(json_string)
    
    #convert payload info in string "json_string" in json format into Python string format
    y = json.loads(json_string) 
    
    print("LOWI's MAC Address: ", y["ident"])
    
    #print MQTT received message's payload, preceeded by date/time stamp - in Central Europe Time (CET) time zone 
    print(dt_eur.strftime("%Y:%m:%d %H:%M:%S %Z")," ", json_string)
    
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


