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
    
    #calculate length / number of characters of message's payload
    payload_length = len(json_string)
    
    #convert payload info in string "json_string" in json format into Python string format
    y = json.loads(json_string) 
    
    #Extract LOWI MAC address info
    LOWI_MAC_address_label = "LOWI's MAC Address: "
    LOWI_MAC_address_data = y["ident"]
    print(LOWI_MAC_address_label, LOWI_MAC_address_data)
    
    #Extract LOWI device channel info
    LOWI_device_channel_label = "LOWI's device channel: "
    LOWI_device_channel_data = y["device_CH"]
    print(LOWI_device_channel_label, LOWI_device_channel_data)
    
    
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


