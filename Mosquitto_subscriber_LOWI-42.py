'''
Created on        24 October 2022
Last updated on   20 November 2022
@author:          Dappeschen
Installation      Elctrical energy meter:
                      SAGEMCOM  
                      EAN 541449400001820905
                      ORES Bemgium
                      installed 19 may 2022
                  Data provider
                      2Wire LOWI3 P1 WIFI Dongel P1 port, Qonnex Belgium, MAC address 3494546c709b
'''

import paho.mqtt.client as mqtt
import time
import datetime
from datetime import datetime
from datetime import date
import pytz                         # for time zone()
import json
 
# Constants, written in upper case 
FILENAME = "received_messages.csv"
TOPIC = "3494546c709b/PUB/CH0"
MQTT_BROKER = "test.mosquitto.org"
CLIENT_ID = "LOWI-42"
HEADERS = ("ident","device_CH","Name","Type","Units","U","I","PI","PE","T","CIH","CIL","CEH","CEL","CG","CW")
# Text formatting constants
GREEN = '\033[92m'                                                            
BLUE = '\033[94m'
ENDC = '\033[0m'  
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
                 
# Date constants
METER_INSTALLATION_DATE = date(2022, 5, 19)

def on_connect(client, userdata, flags, rc):
    # Subscribe after each connect
    client.subscribe(TOPIC)
    
def on_message(client, userdata, message):
    #Date and Tie in Central Europe / Brussels, Belgium
    dt_eur = datetime.now(pytz.timezone('Europe/Brussels'))
    
    #prepare to print MQTT received message's payload 
    json_string = str(message.payload.decode("utf-8"))
    
    #calculate length / number of characters of message's payload
    payload_length = len(json_string)
    
    #convert payload info in string "json_string" in json format into Python string format
    payload_dict = json.loads(json_string) 
    
    #clear Python console
    print('\n' * 150)
     
    print(UNDERLINE + "INSTALLATION" + ENDC)
    print("Meter installation date" + " "*26  + str(METER_INSTALLATION_DATE))
    meter_last_index_reset_date = "19-05-2022"
    print("Meter last index reset date" + " "*22 + meter_last_index_reset_date)
    
    print()
    print()
    
    print(UNDERLINE + "CURRENT" + ENDC)
    
    #Calculate metr operation durations
    today = date.today()
    #today = datetime.now()
    meter_days_in_operation = abs(METER_INSTALLATION_DATE - today)
    #meter_days_since_last_index_reset_date = abs(datetime.strptime(meter_last_index_reset_date, '%d-%m-%Y') - today)
    #Print current date
    print("Date"  + " "*44, dt_eur.strftime("%d-%m-%Y"))
    meter_time_in_operation_str = str(meter_days_in_operation)
    #Print meter total time in operation duration
    print("Meter Total Days in Operation since Installation " + meter_time_in_operation_str[0:8])
    print("Meter Days in Operation since last Index Reset   " + meter_time_in_operation_str[0:8])
    #Print current time
    print("Time" + " "*44, dt_eur.strftime("%H:%M:%S %Z"))
    
    #Get and display counter status for energy imported
    counter_status_energy_imported_low = payload_dict["CIL"]
    counter_status_energy_imported_high = payload_dict["CIH"]
    counter_status_energy_imported = int((int(counter_status_energy_imported_low) + int(counter_status_energy_imported_high)) / 1000)
    print(BLUE + "Counter Status Energy Imported", format(int(counter_status_energy_imported), '22d'), "kWh" + ENDC)
    
    #Get and display counter status for energy exported
    counter_status_energy_exported_low = payload_dict["CEL"]
    counter_status_energy_exported_high = payload_dict["CEH"]
    counter_status_energy_exported = int((int(counter_status_energy_exported_low) + int(counter_status_energy_exported_high)) / 1000)
    print(GREEN + "Counter Status Energy Exported", format(int(counter_status_energy_exported), '22d'), "kWh" + ENDC)
    
    print('-' * 60)
        
    #Calculate and display current energy balance exported - imported
    current_energy_balance = counter_status_energy_exported - counter_status_energy_imported
    if current_energy_balance > 0:
      textcolor = GREEN
      import_export = "+"
    else:
      textcolor = BLUE  
      import_export = "-"
    print(BOLD + textcolor + "Energy Balance" + " "*32 + import_export + format(current_energy_balance,'6d')+ " kWh" + ENDC)    
    
    print('-' * 60)
      
    #display current voltage
    print("Voltage"  + " "*37, format(int(payload_dict["U"]),'7d'), " Volt  " )
    
    #calculate and display current current
    if int(payload_dict["PI"]) > 0:
      textcolor = BLUE
    else:
      textcolor = ENDC  
    print(textcolor + "Current"  + " "*37, format(int(int(payload_dict["I"]) / 1000),'7d'), " Ampere" + ENDC)
    
    #display current imported power
    if int(payload_dict["PI"]) > 0:
      textcolor = BLUE
    else:
      textcolor = ENDC  
    print(textcolor + "Power Import" + " "*32, format(int(payload_dict["PI"]),'7d'), " Watt" + ENDC)
    
    #display current imported power
    if int(payload_dict["PE"]) > 0:
      textcolor = GREEN
    else:
      textcolor = ENDC  
    print("Power Export" + " "*32, format(int(payload_dict["PE"]),'7d'), " Watt")
          
          #,["I"],["PI"],["PE"],["T"],["CIH"],["CIL"],["CEH"],["CEL"],["CG"],["CW"])
    # Clearing the Screen
    #os.system('cls')
   
    
#main    
#Preparing to connect to free MQTT test / broker server MOSQUITTO.org
client = mqtt.Client(CLIENT_ID)


client.subscribe(TOPIC)
client.on_connect=on_connect
client.on_message=on_message 

client.connect(MQTT_BROKER) 

client.loop_forever()

