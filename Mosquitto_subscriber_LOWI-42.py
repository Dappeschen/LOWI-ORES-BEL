'''
Created on        24 October 2022
Last updated on   24 December 2022
@author           Dappeschen
Installation      location
                    rdj241360W
                  electrical energy meter:
                      SAGEMCOM  
                      EAN 541449400001820905
                      ORES Belgium
                      installed 19 May 2022
                  data provider
                      2Wire LOWI3 P1 WIFI Dongel P1 port, Qonnex bvba, 9310 Aalst, Belgium, MAC address 3494546c709b
'''


import paho.mqtt.client as mqtt
import time
import datetime
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import pytz                         # for time zone()
import json
#from numpy import power
 
# Constants
FILENAME =      "received_messages.csv"
TOPIC =         "3494546c709b/PUB/CH0"
MQTT_BROKER =   "test.mosquitto.org"
CLIENT_ID =     "LOWI-42"
HEADERS =       ("ident","device_CH","Name","Type","Units","U","I","PI","PE","T","CIH","CIL","CEH","CEL","CG","CW")
MAINS_REFERENCE_VOLTAGE_LEVEL = 230

# Text formatting constants
GREEN =     '\033[92m'                                                            
BLUE =      '\033[94m'
RED =       '\033[91m'
ENDC =      '\033[0m'  
BOLD =      '\033[1m'
BLINK =     '\033[5m'
UNDERLINE = '\033[4m'
                 
# Date constants
METER_INSTALLATION_DATE = date(2022, 5, 19)


def on_connect(client, userdata, flags, rc):
    # Subscribe after each connect
    client.subscribe(TOPIC)
    
def on_message(client, userdata, message):
    # Date and Tie in Central Europe / Brussels, Belgium
    dt_eur = datetime.now(pytz.timezone('Europe/Brussels'))
    
    # prepare to print MQTT received message's payload 
    json_string = str(message.payload.decode("utf-8"))
    
    # convert payload info in string "json_string" in JSON format into Python string format
    payload_dict = json.loads(json_string) 
    
    # clear Python console
    print('\n' * 150)
     
    print(UNDERLINE + "INSTALLATION" + ENDC)
    print("Meter installation date" + " "*26  + str(METER_INSTALLATION_DATE))
    meter_last_index_reset_date = date(2022, 5, 19)
    meter_last_index_reset_date_str = str(meter_last_index_reset_date)
    print("Meter last index reset date" + " "*22 + meter_last_index_reset_date_str)
       
    print()
    print()
    
    print(UNDERLINE + "CURRENT" + ENDC)
    
    # Calculate metr operation durations
    today = date.today()
    today_str = str(today)
    # today = datetime.now()
    meter_total_days_in_operation = abs(METER_INSTALLATION_DATE - today)
    # Print current date
    print("Date"  + " "*44, str(today))
    meter_total_days_in_operation_str = str(meter_total_days_in_operation)
    meter_total_months_in_operation = meter_total_days_in_operation/ 30
    
    # Print current time
    print("Local time last measurement" + " "*21, dt_eur.strftime("%H:%M:%S %Z"))
    
    # Print meter total time in operation duration
    print("Meter total days in operation since Installation " + meter_total_days_in_operation_str[0:8])
    
    meter_days_in_operation_since_last_reset = abs(meter_last_index_reset_date - today)
    meter_days_in_operation_since_last_reset_str = str(meter_days_in_operation_since_last_reset)
    print(" "*6 + "days in operation since last Index Reset   " + meter_days_in_operation_since_last_reset_str[0:8])
    
    meter_next_index_reset_date = meter_last_index_reset_date + relativedelta(years=1)
    meter_next_index_reset_date_str = str(meter_next_index_reset_date)
    print(" "*6 + "next reset date " + " "*27 + meter_next_index_reset_date_str)
    
    # Calculate and print time remaining until next annual meter index 'reset' date 
    date_1 = today_str
    date_2 = meter_next_index_reset_date_str
    
    start = datetime.strptime(date_1, "%Y-%m-%d")
    end =   datetime.strptime(date_2, "%Y-%m-%d") 
    diff = end.date() - start.date()
    diff_int = int(diff.days)
    print(" "*6 + "days until next reset" + " "*22 + str(diff_int) + " days")
    
    meter_days_in_operation_until_next_reset = meter_next_index_reset_date - relativedelta(days = 4)
    
    # Get data, calculate and display meter status / index for energy imported
    meter_status_energy_imported_low = payload_dict["CIL"]
    meter_status_energy_imported_high = payload_dict["CIH"]
    meter_status_energy_imported = int((int(meter_status_energy_imported_low) + int(meter_status_energy_imported_high)) / 1000)
    print(BLUE + " "*6 + "counter reading energy imported", format(int(meter_status_energy_imported), '15d'), "kWh" + " "*10 + "retrieved from grid" + ENDC)
    
    # Get data, calculate and display meter status / index for energy imported
    meter_status_energy_exported_low = payload_dict["CEL"]
    meter_status_energy_exported_high = payload_dict["CEH"]
    meter_status_energy_exported = int((int(meter_status_energy_exported_low) + int(meter_status_energy_exported_high)) / 1000)
    print(GREEN + " "*29 + "exported", format(int(meter_status_energy_exported), '15d'), "kWh" + " "*10 + "injected into energy distribution grid since meter installation date" + ENDC)
    
    delta_meter_status = meter_status_energy_exported - meter_status_energy_imported
    print(" "*29 + "delta" + " "*4 + format(int(delta_meter_status), '15d'), "kWh" + " "*10 + "export - import")
    
    # Print a line of dashes
    print('-' * 140)
        
    # Calculate and display current energy balance exported - imported
    current_energy_balance = meter_status_energy_exported - meter_status_energy_imported
    if current_energy_balance > 0:
      text_color = GREEN
      import_export = "+"
    else:
      text_color = BLUE  
      import_export = "-"
    print(BOLD + text_color + " "*6 + "Energy balance remaining til next reset" + " "*2 + UNDERLINE + import_export + format(current_energy_balance,'5d') + " kWh" + ENDC + text_color + BOLD + " "*10 + "still available free of charge from the grid as 'a battery' / buffer" + ENDC)    
    print(text_color + " "*46 + format(abs(int(current_energy_balance / diff_int)), '7d') + " kWh" + " "*10 + "per day" + ENDC)    
    
    # Print a line of dashes
    print('-' * 140)
      
    # Display current mains voltage and variance
    mains_voltage = int(payload_dict["U"])
    mains_voltage_variance = mains_voltage - MAINS_REFERENCE_VOLTAGE_LEVEL
    if mains_voltage_variance > 0: 
       mains_voltage_variance_posneg = "+"
    else:
       mains_voltage_variance_posneg = ""
    
    if mains_voltage_variance > 10: 
       text_color = RED
    elif mains_voltage_variance < -10:
       text_color = RED
    else:
        text_color = ENDC
    print(" "*6 + "Voltage"  + " "*31, format(mains_voltage,'7d'), " V" + " "*12 + text_color + "(Variance - ref. 230V normal: " + mains_voltage_variance_posneg + str(mains_voltage_variance) + "V)" + ENDC)
    
    # Calculate and display current current
    current = int(payload_dict["I"])/1000
    if current > 0 and (int(payload_dict["PI"])) > 0 :
      text_color = BLUE
      current_flow_direction = "currently flowing from the public energy grid into the house"
    else:
      text_color = GREEN  
      #current = format(str(int(int(payload_dict["PE"]) / int(payload_dict["U"]))),'7d')
      current = int(payload_dict["PE"]) / int(payload_dict["U"])
      current_flow_direction = "currently flowing from the house into the public energy grid"
    print(text_color + " "*6 + "Current"  + " "*33, '{:05.2f}'.format(current) + "  A" + " "*12 + current_flow_direction + ENDC)
    
    # Display current net power value exported / exported
    if int(payload_dict["PI"]) > 0:
      current_power = int(payload_dict["PI"])
      text_color = BLUE
      power_mode ="Import"
      solar_generation_message = ""
    else:
      current_power = int(payload_dict["PE"])
      text_color = GREEN
      power_mode ="Export"  
      solar_generation_message = "currently not self-consumed"
    print(text_color + " "*6 + "Power " + power_mode + " "*28 + format(current_power,'7d'), "W" + " "*12 + solar_generation_message + ENDC)
    
            
def main():
    client = mqtt.Client(CLIENT_ID)
    
    client.subscribe(TOPIC)
    
    client.on_connect=on_connect
    
    client.on_message=on_message 
    
    client.connect(MQTT_BROKER) 
    
    client.loop_forever()


# Main    
if __name__ == "__main__":
    main()

