'''
Created on            10 July 2023
Last updated on       10 July 2023
@author               Dappeschen
Installation          location
                        rdj241360W
                      data providers
                        - 2-Wire WIFI smart plug 'WP16A', Qonnex bvba, 9310 Aalst, Belgium, 2-wire.net
                        - 2-Wire WIFI P1 dongle 'LOWI3', Qonnex bvba, 9310 Aalst, Belgium, 2-wire.net
                      data broker / MQTT
                        - local Raspberry pi on home LAN: 192.168.0.X
Programming language  Python, v3
IDE                   Eclipse, pydev
Project description   the LOWI3 electrical energy meter WIFI dongle and the 230V WIFI smart plug 'WP16A'  by Qonnex / 2-Wire, Belgium (2-wire.net) uses the MQTT protocol.
                      The LOWI and the plug send energy meter data to an MQTT broker / server.
                      The plug furthermore gets state-toggled / switched on and off via the MQTT protocol from an external switch.
                      The project aims to display key meter data in the Python text console for the LOWI and the plug and to toggle the plug status on / off:
                      - pressing the keyboard key '1' switches the plug on
                      - pressing the keyboard key '0' switches the plug off
                      Pressing the keyboard key 'e' ends the program.
Code focus            GUI via tkinter and reading data from the Qonnex LOWI3 and the smart plug and writing / publishing / sending data to the plug in parallel 
                      (to switch plug on / off)
Code Inspirations     https://techtutorialsx.com/2017/04/14/python-publishing-messages-to-mqtt-topic/
(selected)            http://www.steves-internet-guide.com/multiple-client-connections-python-mqtt/
'''

#import libraries / modules
import paho.mqtt.client as mqttClient
import time
import datetime
from   datetime import datetime
from   datetime import date
from   dateutil.relativedelta import relativedelta
import pytz                         # for time zone()
import json
import keyboard
from   tkinter import *
import tkinter.font as tkFont
from   mttkinter import *
from   tkinter import ttk
from   tkinter import messagebox
import threading
from   cProfile import label
import sys

        
#define constants
MQTT_BROKER =                       "mqtt.flespi.io"                                                    # MQTT broker server URL
MQTT_TOKEN =                        "PUT YOUR FLESPI.IO SERVER / BROKER TOKEN VALUE HERE"               # token to log into free MQTT broker account flespi.io. Serves as account's User Name / ID
MQTT_PW =                           "PUT YOUR FLESPI.IO SERVER / BROKER USER PASSWORD HERE"             # password to log into MQTT broker account
PLUG_TOPIC_READ =                   "PLUG SERIAL NUMBER/PUB/CH1"                                        # smart plug's data read path
PLUG_TOPIC_WRITE =                  "PLUG SERIAL NUMBER/SET/REL/CH1"                                    # smart plug's data write path
LOWI_TOPIC =                        "LOWI SERIAL NUMBER/PUB/CH0"                                        # LOWI energy meter dongle's data read path 
LOWI_HEADERS =                      ("ident","device_CH","Name","Type","Units", "U","I","PI","PE","T",
                                     "CIH","CIL","CEH","CEL","CG","CW")
MAINS_REFERENCE_VOLTAGE_LEVEL =     230                                                                 # 230V AC standard reference voltage on electrical energy grid 
                                                                                                        # in Central Continental Europe
LOWI_Device_METER_INSTALLATION_DATE = date(2022, 5, 19)
LOWI_DEVICE_METER_LAST_INDEX_RESET_DATE = date(2023, 5, 31)

LOWI_DEVICE_METER_LAST_INDEX_IMPORT_HIGH = 1701   # consumption index 'high' @ last index reset date
LOWI_DEVICE_METER_LAST_INDEX_IMPORT_LOW = 1883    # consumption index 'low'  @ last index reset date
LOWI_DEVICE_METER_LAST_INDEX_IMPORT_TOTAL = LOWI_DEVICE_METER_LAST_INDEX_IMPORT_HIGH + LOWI_DEVICE_METER_LAST_INDEX_IMPORT_LOW # total consumption index @ last index reset date
LOWI_DEVICE_METER_LAST_INDEX_EXPORT_HIGH = 3405    # injection index 'high'   @ last index reset date
LOWI_DEVICE_METER_LAST_INDEX_EXPORT_LOW = 1286    # injection index 'low'    @ last index reset date
LOWI_DEVICE_METER_LAST_INDEX_EXPORT_TOTAL = LOWI_DEVICE_METER_LAST_INDEX_EXPORT_HIGH + LOWI_DEVICE_METER_LAST_INDEX_EXPORT_LOW  # total injection index  @ last index reset date


# Text formatting constants
GREEN =     '\033[92m'                                                            
BLUE =      '\033[94m'
RED =       '\033[91m'
ENDC =      '\033[0m'  
BOLD =      '\033[1m'
BLINK =     '\033[5m'
UNDERLINE = '\033[4m'

# connect function triggered on connect message from Qonnex smart plug to read metered consumption data
def PLUG_on_connect_read(client_read, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker to read PLUG data")
        global PLUG_Connected_read                                               #Use global variable
        PLUG_Connected_read = True                                               #Signal connection 
        client_read.subscribe(PLUG_TOPIC_READ)
    else:
        print("Connection failed to read")


# connect function triggered on connect message from Qonnex smart plug to write data / toggle switch on / off
def PLUG_on_connect_write(client_write, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker to write PLUG data")
        global PLUG_Connected_write                                              #Use global variable
        PLUG_Connected_write = True                                              #Signal connection 
    else:
        print("Connection failed to write")


# connect function triggered on connect message from LOWI meter dongle to read data
def LOWI_on_connect_read(client, userdata, flags, rc):
    # Provide user name = Token and password to access MQTT broker service / account
    client.username_pw_set(username = MQTT_TOKEN, password = MQTT_PW)
    # Subscribe after each connect
    client.subscribe(LOWI_TOPIC)

    
#function triggered when energy meter data published by Qonnex smart plug to MQTT broker for reading / displaying 
def PLUG_on_message_read(client_read, userdata, message):
    
    # clear PLUG text widget
    clear_GUI_text_widget_PLUG('1.0', END)
    
    # print empty line
    string_to_print = ""
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    
    string_to_print = "SMART-PLUG "
    print(UNDERLINE + string_to_print + ENDC)
    print_GUI_PLUG(string_to_print)
    
    #get and display current time
    curr_time = time.strftime("%H:%M:%S", time.localtime())     
    #display current time
    
    string_to_print = "Time               " + curr_time
    print( string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Time               " + curr_time)
    
    # prepare to print MQTT received message's payload 
    PLUG_READ_json_string = str(message.payload.decode("utf-8"))
    # convert pay load info in string "json_string" in JSON format into Python string format
    PLUG_READ_payload_dict = json.loads(PLUG_READ_json_string)
    
    #transfer JSON-format dictionary values to string variables for later display  
    PLUG_READ_Device_ID                = PLUG_READ_payload_dict["ident"]
    PLUG_READ_Device_Channel           = PLUG_READ_payload_dict["device_CH"]
    PLUG_READ_Device_Name              = PLUG_READ_payload_dict["Name"]
    PLUG_READ_Device_Type              = PLUG_READ_payload_dict["Type"]
    PLUG_READ_Device_Relay_Status      = PLUG_READ_payload_dict["REL"]
    PLUG_READ_Device_Voltage           = PLUG_READ_payload_dict["U"]
    PLUG_READ_Device_Current           = PLUG_READ_payload_dict["I"]
    PLUG_READ_Device_Power             = PLUG_READ_payload_dict["P"]
    PLUG_READ_Device_Meter_Status_High = PLUG_READ_payload_dict["CH"]
    PLUG_READ_Device_Meter_Status_Low  = PLUG_READ_payload_dict["CL"]
    PLUG_READ_Device_RSSI              = PLUG_READ_payload_dict["RSSI"]
        
    #print JSON string contents of the PLUG meter's parameters  - just for debugging / parameter value control 
    string_to_print = PLUG_READ_json_string
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print(PLUG_READ_json_string)
    
    # insert empty line
    string_to_print = ""
    print(string_to_print)
    print_GUI_PLUG(string_to_print) 
    
    #display main plug meter data
    string_to_print = "Plug Device"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Plug Device")
    
    PLUG_READ_Device_Relay_Status_str = "OFF"
    if PLUG_READ_Device_Relay_Status == "1":
        PLUG_READ_Device_Relay_Status_str = "ON"
    if PLUG_READ_Device_Relay_Status == "0":
        PLUG_READ_Device_Relay_Status_str = "OFF"    
    
    string_to_print = "Status              " + PLUG_READ_Device_Relay_Status_str
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Status              " + PLUG_READ_Device_Relay_Status_str)
    
    string_to_print = "Voltage             " + PLUG_READ_Device_Voltage +" V"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Voltage             " + PLUG_READ_Device_Voltage +" V")
    
    string_to_print = "Current             " + PLUG_READ_Device_Current + " mA"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Current             " + PLUG_READ_Device_Current + " mA")
    
    PLUG_READ_Device_Power_float = int(PLUG_READ_Device_Current)/ 1000 * int(PLUG_READ_Device_Voltage)
    string_to_print = "Power               " + str("%.2f" % PLUG_READ_Device_Power_float) + " W"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Power               " + str("%.2f" % PLUG_READ_Device_Power_float) + " W")
    #print("Power              " + str(int(Device_Power) * 100))              #"parameter "P" in JSON payload seems to always be '0'.... Not working?
    
    string_to_print = "Meter Status High   " + PLUG_READ_Device_Meter_Status_High + " Wh"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Meter Status High   " + PLUG_READ_Device_Meter_Status_High + " kWh")
    
    string_to_print = "Meter Status Low    " + PLUG_READ_Device_Meter_Status_Low + " Wh"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("Meter Status Low    " + PLUG_READ_Device_Meter_Status_Low + " kWh")
    
    string_to_print = "WIFI Signal         " + PLUG_READ_Device_RSSI + " dBm"
    print(string_to_print)
    print_GUI_PLUG(string_to_print)
    #print("WIFI Signal         " + PLUG_READ_Device_RSSI + " dBm")


def print_GUI_temp():
    string_to_print = LOWI_Device_payload_dict["ident"] + " / " + LOWI_Device_payload_dict["Name"] +" / " + LOWI_Device_payload_dict["device_CH"] 
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '2.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('2.0 + 51 chars', to_position_str)
    text_LOWI.insert('2.0 + 51 chars', string_to_print)


#function to define, format and display LOWI meter data, whenever message is received from / sent by LOWI dongle (to / via MQTT broker / server)
def LOWI_on_message(client, userdata, message):
    
    # Date and Tie in Central Europe / Brussels, Belgium
    dt_eur = datetime.now(pytz.timezone('Europe/Brussels'))
    
    # prepare to print MQTT received message's payload 
    LOWI_Device_json_string = str(message.payload.decode("utf-8"))
    
    # convert payload info in string "json_string" in JSON format into Python string format
    LOWI_Device_payload_dict = json.loads(LOWI_Device_json_string) 
         
    
    string_to_print = LOWI_Device_payload_dict["ident"] + " / " + LOWI_Device_payload_dict["Name"] +" / " + LOWI_Device_payload_dict["device_CH"] 
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '2.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('2.0 + 51 chars', to_position_str)
    text_LOWI.insert('2.0 + 51 chars', string_to_print)
    
   
    string_to_print = str(LOWI_Device_METER_INSTALLATION_DATE)
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '3.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('3.0 + 51 chars', to_position_str)
    text_LOWI.insert('3.0 + 51 chars', string_to_print)
    
    #LOWI_Device_meter_last_index_reset_date = date(2022, 5, 19)
    LOWI_Device_meter_last_index_reset_date_str = str(LOWI_DEVICE_METER_LAST_INDEX_RESET_DATE)
    
    string_to_print = LOWI_Device_meter_last_index_reset_date_str
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '4.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('4.0 + 51 chars', to_position_str)
    text_LOWI.insert('4.0 + 51 chars', string_to_print)
    
    
    # Calculate meter operation durations
    today = date.today()
    today_str = str(today)
    # today = datetime.now()
    LOWI_Device_meter_total_days_in_operation = abs(LOWI_Device_METER_INSTALLATION_DATE - today)
    
    # Display current date
    string_to_print = str(today)
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '7.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('7.0 + 51 chars', to_position_str)
    text_LOWI.insert('7.0 + 51 chars', string_to_print)
    
    # Display current time
    string_to_print = dt_eur.strftime("%H:%M:%S %Z")
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '8.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('8.0 + 51 chars', to_position_str)
    text_LOWI.insert('8.0 + 51 chars', string_to_print)
    
        
    # Display meter total time in operation duration
    LOWI_Device_meter_total_days_in_operation_str = str(LOWI_Device_meter_total_days_in_operation)
    LOWI_Device_meter_total_months_in_operation = LOWI_Device_meter_total_days_in_operation/ 30
    string_to_print = LOWI_Device_meter_total_days_in_operation_str[0:8]
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '9.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('9.0 + 51 chars', to_position_str)
    text_LOWI.insert('9.0 + 51 chars', string_to_print)
    
    
    # Calculate and display meter time in operation since last index reset date
    LOWI_Device_meter_days_in_operation_since_last_reset = abs(LOWI_DEVICE_METER_LAST_INDEX_RESET_DATE - today)
    LOWI_Device_meter_days_in_operation_since_last_reset_str = str(LOWI_Device_meter_days_in_operation_since_last_reset)
    string_to_print = LOWI_Device_meter_days_in_operation_since_last_reset_str[0:8]
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '10.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('10.0 + 51 chars', to_position_str)
    text_LOWI.insert('10.0 + 51 chars', string_to_print)
    
    # Display next index reset date
    LOWI_Device_meter_next_index_reset_date = LOWI_DEVICE_METER_LAST_INDEX_RESET_DATE + relativedelta(years=1)
    LOWI_Device_meter_next_index_reset_date_str = str(LOWI_Device_meter_next_index_reset_date)
    string_to_print = LOWI_Device_meter_next_index_reset_date_str
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '11.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('11.0 + 51 chars', to_position_str)
    text_LOWI.insert('11.0 + 51 chars', string_to_print)
    
    # Calculate and display time remaining until next annual meter index 'reset' date 
    date_1 = today_str
    date_2 = LOWI_Device_meter_next_index_reset_date_str
    start = datetime.strptime(date_1, "%Y-%m-%d")
    end =   datetime.strptime(date_2, "%Y-%m-%d") 
    diff = end.date() - start.date()
    diff_int = int(diff.days)
    string_to_print = str(diff_int)
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '12.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('12.0 + 51 chars', to_position_str)
    text_LOWI.insert('12.0 + 51 chars', string_to_print)
    
    #LOWI_Device_meter_days_in_operation_until_next_reset = LOWI_Device_meter_next_index_reset_date - relativedelta(days = 4)
    
    # Get data, calculate and display meter status / index for energy imported since initial meter installation date
    LOWI_Device_meter_status_energy_imported_low = LOWI_Device_payload_dict["CIL"]
    LOWI_Device_meter_status_energy_imported_high = LOWI_Device_payload_dict["CIH"]
    LOWI_Device_meter_status_energy_imported = int((int(LOWI_Device_meter_status_energy_imported_low) + int(LOWI_Device_meter_status_energy_imported_high)) / 1000)
    
    string_to_print = format(int(LOWI_Device_meter_status_energy_imported), '4d')
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '13.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('13.0 + 51 chars', to_position_str)
    text_LOWI.insert('13.0 + 51 chars', string_to_print)
    
    # Get data, calculate and display meter status / index for energy exported since initial meter installation date
    LOWI_Device_meter_status_energy_exported_low = LOWI_Device_payload_dict["CEL"]
    LOWI_Device_meter_status_energy_exported_high = LOWI_Device_payload_dict["CEH"]
    LOWI_Device_meter_status_energy_exported = int((int(LOWI_Device_meter_status_energy_exported_low) + int(LOWI_Device_meter_status_energy_exported_high)) / 1000)
    string_to_print = format(int(LOWI_Device_meter_status_energy_exported), '4d')
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '14.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('14.0 + 51 chars', to_position_str)
    text_LOWI.insert('14.0 + 51 chars', string_to_print)
    
    #Calculate and display remaining delta export - import since initial meter installation date
    LOWI_Device_delta_meter_status = LOWI_Device_meter_status_energy_exported - LOWI_Device_meter_status_energy_imported
   
    string_to_print = format(int(LOWI_Device_delta_meter_status),'4d')
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '15.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('15.0 + 51 chars', to_position_str)
    text_LOWI.insert('15.0 + 51 chars', string_to_print)
    
        
    # Calculate and display current energy balance exported - imported  since last meter reset date
    LOWI_DEVICE_METER_LAST_INDEX_DELTA = LOWI_DEVICE_METER_LAST_INDEX_EXPORT_TOTAL - LOWI_DEVICE_METER_LAST_INDEX_IMPORT_TOTAL
    
    LOWI_Device_current_energy_balance = (LOWI_Device_meter_status_energy_exported - LOWI_DEVICE_METER_LAST_INDEX_EXPORT_TOTAL) - (LOWI_Device_meter_status_energy_imported - LOWI_DEVICE_METER_LAST_INDEX_IMPORT_TOTAL)
    
    if LOWI_Device_current_energy_balance > 0:
      text_color = GREEN
      text_widget_color = "green"
      LOWI_Device_import_export = "+"
    else:
      text_color = RED  
      text_widget_color = "red"
      LOWI_Device_import_export = "-"
    
    string_to_print = LOWI_Device_import_export + format(LOWI_Device_current_energy_balance,'3d')
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '17.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('17.0 + 51 chars', to_position_str)
    text_LOWI.insert('17.0 + 51 chars', string_to_print, text_widget_color)
    
    #to avoid divison by zero error
    if diff_int == 0:
        diff_int = 1
        
    string_to_print = format(abs(int(LOWI_Device_current_energy_balance / diff_int)), '4d')
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '18.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('18.0 + 51 chars', to_position_str)
    text_LOWI.insert('18.0 + 51 chars', string_to_print, text_widget_color)
    
    # Display current mains voltage and variance
    LOWI_Device_mains_voltage = int(LOWI_Device_payload_dict["U"])
    LOWI_Device_mains_voltage_variance = LOWI_Device_mains_voltage - MAINS_REFERENCE_VOLTAGE_LEVEL
    if LOWI_Device_mains_voltage_variance > 0: 
       LOWI_Device_mains_voltage_variance_posneg = "+"
    else:
       LOWI_Device_mains_voltage_variance_posneg = ""
    
    if LOWI_Device_mains_voltage_variance > 10: 
       text_color = RED
    elif LOWI_Device_mains_voltage_variance < -10:
       text_color = RED
    else:
        text_color = ENDC
    
    string_to_print = format(LOWI_Device_mains_voltage,'3d')
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '20.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('20.0 + 51 chars', to_position_str)
    text_LOWI.insert('20.0 + 51 chars', string_to_print)
    
    string_to_print = str(LOWI_Device_mains_voltage_variance_posneg) + str(LOWI_Device_mains_voltage_variance) +" V"
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '20.0 + 94 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('20.0 + 94 chars', to_position_str)
    text_LOWI.insert('20.0 + 94 chars', string_to_print)
    
    
    # Calculate and display current current
    LOWI_Device_current = int(LOWI_Device_payload_dict["I"])/1000
    if LOWI_Device_current > 0 and (int(LOWI_Device_payload_dict["PI"])) > 0 :
      text_color = BLUE
      LOWI_Device_current_flow_direction = "currently flowing from the public energy grid into the house"
    else:
      text_color = GREEN  
      #current = format(str(int(int(payload_dict["PE"]) / int(payload_dict["U"]))),'7d')
      LOWI_Device_current = int(LOWI_Device_payload_dict["PE"]) / int(LOWI_Device_payload_dict["U"])
      LOWI_Device_current_flow_direction = "currently flowing from the house into the public energy grid"
    
    string_to_print = '{:04.1f}'.format(LOWI_Device_current) + " A      " + LOWI_Device_current_flow_direction
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '21.0 + 51 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('21.0 + 51 chars', to_position_str)
    text_LOWI.insert('21.0 + 51 chars', string_to_print)
    
 
    # Display current net power value exported / exported
    if int(LOWI_Device_payload_dict["PI"]) > 0:
      LOWI_Device_current_power = int(LOWI_Device_payload_dict["PI"])
      text_color = RED
      text_widget_color = "red"
      text_LOWI.tag_configure("color", foreground="red")
      LOWI_Device_power_mode ="Import"
      LOWI_Device_solar_generation_message = "from the public energy grid"
    else:
      LOWI_Device_current_power = int(LOWI_Device_payload_dict["PE"])
      text_color = GREEN
      text_widget_color = "green"
      text_LOWI.tag_configure("color", foreground=text_widget_color)
      #text_LOWI.tag_configure("color", foreground="green")
      
      LOWI_Device_power_mode ="Export"  
      LOWI_Device_solar_generation_message = "currently not self-consumed"
    
    string_to_print = LOWI_Device_power_mode + " "*30 + format(LOWI_Device_current_power,'7d') + " W" + " "*6 + LOWI_Device_solar_generation_message
    string_length = len(string_to_print)
    string_length_str = str(string_length)
    to_position_str = '22.0 + 12 chars + ' + string_length_str + ' chars'
    text_LOWI.delete('22.0 + 12 chars', to_position_str)
    
    text_LOWI.insert('22.0 + 12 chars', string_to_print, "color")
    
    text_LOWI.tag_configure("bold", font=("Courier", 10, "bold"))
    #text_LOWI.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
    text_LOWI.tag_add("bold", "22.0 + 12 chars", to_position_str)
    
    
# function to clear Python's text output console 
def clear_console():                                            
    print('\n' * 250)


# function to create text widget in GUI
def GUI_text_widget_LOWI(widget_reference, widget_width, widget_hight):
    global text_LOWI
    text_LOWI = Text(GUI, width = widget_width , height = widget_hight)
    text_LOWI.pack()
    
# function to create text widget in GUI
def GUI_text_widget_PLUG(widget_reference, widget_width, widget_hight):
    global text_PLUG
    text_PLUG = Text(GUI, width = widget_width , height = widget_hight)
    text_PLUG.pack()


# function to create label widget in GUI
def GUI_label_widget(label_reference):
    label_text = label_reference
    l = Label(GUI, text = label_text)
    l.config(font =("TkDefaultFont", 14))
    #l.config(font =("Courier", 14)) 
    l.pack()

# function to delete text content of GUI's LOWI text widget
def clear_GUI_text_widget_LOWI(start_position, end_position):
    start_position_delete = start_position
    end_position_delete = end_position
    #text['state'] = 'normal'
    text_LOWI.delete(start_position_delete, end_position_delete)
    #text.delete('1.0', END)
    #text['state'] = 'disabled'

# function to delete text content of GUI's PLUG text widget
def clear_GUI_text_widget_PLUG(start_position, end_position):
    start_position_delete = start_position
    end_position_delete = end_position
    #text['state'] = 'normal'
    text_PLUG.delete(start_position_delete, end_position_delete)
    #text.delete('1.0', END)
    #text['state'] = 'disabled'


# function to write text into GUI's LOWI text widget and end of current text, followed by line break
def print_GUI_LOWI(GUI_text_string):
    #text['state'] = 'normal'
    GUI_text_to_print = GUI_text_string
    #text_widget_font =  tkFont.Font(family="Arial", size=16, weight="bold", slant="italic")
    #text.configure(font=text_widget_font)
    #textExample.configure(font=fontExample)
    text_LOWI.insert(END, GUI_text_to_print + '\n')
    #text['state'] = 'disabled'


def print_text_mask_GUI_LOWI():
    #text['state'] = 'normal'
    #GUI_text_to_print = GUI_text_string
    #text_widget_font =  tkFont.Font(family="Arial", size=16, weight="bold", slant="italic")
    #text.configure(font=text_widget_font)
    #textExample.configure(font=fontExample)
    #text_LOWI.insert(END, GUI_text_to_print + '\n')
    #text['state'] = 'disabled'

    #clear text widget completely
    clear_GUI_text_widget_LOWI(1.0, END)
    
    #create the text screen mask, by creating a formatted string, which contains all static text, like parameter labels, etc...
    string_to_print = "METER INSTALLATION" + "\n" 
    text_LOWI.insert('1.0', string_to_print)
    
    #make block heading bold
    string_length_str = str(len(string_to_print))
    to_position_str = '1.0 + ' + string_length_str + ' chars'
    text_LOWI.tag_configure("bold", font=("Courier", 10, "bold"))
    text_LOWI.tag_add("bold", "1.0", to_position_str)
    
    string_to_print = "Metered data IDs" + " "*80 + "\n" + \
    "Meter installation date" + " "*36  + " "*4 + "Meter initial index 'Import':    0kWh  Meter initial index 'Export':    0kWh" + "\n" + \
    "Meter last index reset date" +  " "*32 + " "*4 + "Meter last reset index 'Import': " + str(LOWI_DEVICE_METER_LAST_INDEX_IMPORT_TOTAL) +  "  Meter last reset index 'Export': " + str(LOWI_DEVICE_METER_LAST_INDEX_EXPORT_TOTAL) + "(Delta: " + str(LOWI_DEVICE_METER_LAST_INDEX_EXPORT_TOTAL - LOWI_DEVICE_METER_LAST_INDEX_IMPORT_TOTAL) + " kWh)" + "\n" + \
    "\n" + \
    "CURRENT METER MEASURES" + "\n"
    text_LOWI.insert('6.0', string_to_print)
    
    #make block heading bold
    string_length_str = str(len(string_to_print))
    to_position_str = '6.0 + ' + string_length_str + ' chars'
    text_LOWI.tag_configure("bold", font=("Courier", 10, "bold"))
    text_LOWI.tag_add("bold", "6.0", "6.30")
    
    
    string_to_print = "Date"  + " "*80 + "\n" + \
    "Local time last measurement" + " "*80 + "\n" + \
    "Meter total days in operation since Installation " + " "*80 + "\n" + \
    " "*6 + "days in operation since last Index Reset "  + " "*80 + "\n" + \
    " "*6 + "next reset date " + " "*80 + "\n" + \
    " "*6 + "days until next reset" + " "*80 + "\n" + \
    " "*6 + "counter reading energy imported " + "                 " + " kWh" + " "*4 + "retrieved from grid since meter installation date" "\n" + \
    " "*6 + "                       exported " + "                 " + " kWh" + " "*4 + "injected into energy distribution grid since meter installation date" + "\n" + \
    " "*29 + "delta" + " "*4 + "                 " + " kWh" + " "*4 + "export - import" + "\n" + \
    "-" * 140 + "\n"
    text_LOWI.insert('7.0', string_to_print)
    
    
    string_to_print =     " "*6 + "energy balance last reset -> next reset" + " "*4 + "       kWh" + " "*4 + "still available free of charge from the grid as 'battery'" + "\n" + \
    " "*46 + " "           + "         kWh" + " "*4 + "per day" + "\n" + \
    "-" * 140 + "\n" + \
    " "*6 + "voltage"  + " "*42 + " V" + " "*6 + "(Variance - ref. 230V normal: " + " "*5 + ")" + "\n" + \
    " "*6 + "current"  + " "*110 + "\n" + \
    " "*6 + "power " + " "*57 + " W"
    
    #print / insert / display the text string 'string_to_print' with all the fix-text parameter labels in the text widget    
    text_LOWI.insert('17.0', string_to_print)
    
    #make block heading bold
    string_length_str = str(len(string_to_print))
    to_position_str = '17.0 + ' + string_length_str + ' chars'
    text_LOWI.tag_configure("bold", font=("Courier", 10, "bold"))
    text_LOWI.tag_add("bold", "17.0", "17.60")
    
    
# function definition to display / print all variable data parameter values from 2-Wire LOWI meter dongle on screen / into GUI     
def print_variable_GUI_LOWI(text_position, GUI_text_string):
    string_print_position = text_position
    #text['state'] = 'normal'
    GUI_text_to_print = GUI_text_string
    #text_widget_font =  tkFont.Font(family="Arial", size=16, weight="bold", slant="italic")
    #text.configure(font=text_widget_font)
    #textExample.configure(font=fontExample)
    text_LOWI.insert(string_print_position, GUI_text_to_print)
    #text['state'] = 'disabled'


# function to write text into GUI's PLUG text widget and end of current text, followed by line break
def print_GUI_PLUG(GUI_text_string):
    #text['state'] = 'normal'
    GUI_text_to_print = GUI_text_string
    #text_widget_font =  tkFont.Font(family="Arial", size=16, weight="bold", slant="italic")
    #text.configure(font=text_widget_font)
    #textExample.configure(font=fontExample)
    text_PLUG.insert(END, GUI_text_to_print + '\n')
    
    #text['state'] = 'disabled'

#function to be executed on an tkinter-intercepted / -handled keyboard stroke
def onKeyPress(event):
    # for sending / writing data / toggling smart plug status upon keyboard key press
    # 1 = switch plug on
    # 0 = switch plug off
    # e = program end 
    # w = delete GUI's text widget contents / text
    
    keyboard_stroke_value = event.char 
    
    if keyboard_stroke_value == "1" :
       keyboard_stroke_value = "ON"                                                 #set keyboard_stroke_value to ON to switch plug on
       client_PLUG_write.publish(PLUG_TOPIC_WRITE,keyboard_stroke_value)
       
    elif keyboard_stroke_value == "0":
       keyboard_stroke_value = "OFF"                                                #set keyboard_stroke_value to OFF to switch plug off
       client_PLUG_write.publish(PLUG_TOPIC_WRITE,keyboard_stroke_value)
       
    elif keyboard_stroke_value == "w":
       keyboard_stroke_value = " "
       clear_GUI_text_widget_LOWI('1.0', END)                                       # wipe / delete text in GUI text widget
                
    elif keyboard_stroke_value == "e" or keyboard_stroke_value == "q" or keyboard_stroke_value == "Q" or keyboard_stroke_value == "Ctrl-Q" or keyboard_stroke_value == "x":                                               #if key 'e' pressed, then quit program
        GUI.quit()
        GUI.destroy()
        keyboard_stroke_value = "END"  
        disconnect_and_stop_device_loops()
        clear_console() 
        
    
def disconnect_and_stop_device_loops():          
    client_PLUG_read.disconnect()                                #disconnect read connection
    client_PLUG_read.loop_stop()                                 #end read loop
    client_PLUG_write.disconnect()                               #disconnect read connection
    client_PLUG_write.loop_stop()                                #end write loop
    client_LOWI_read.disconnect()
    client_LOWI_read.loop_stop()

def show_info_about_message():
    PythonScripRef_str = sys.argv[0]
    print(PythonScripRef_str)
    messagebox.showinfo(title="About", message='Ideated and created by Doedelchen\n'
                                                'artWare solutions\n'
                                                'All rights reserved 2023\n'
                                                '\n' + 
                                                PythonScripRef_str) 
    
    
# main program body starts here

# create tkinter object 'GUI' to display GUI Window 
GUI = Tk()

# get screen width and height
ws = GUI.winfo_screenwidth()    # get screen width
hs = GUI.winfo_screenheight()   # get screen height
w = ws                          # width for GUI window
h = hs                          # height for GUI window

#w = ws / 1.2                   # width for GUI window
#h = hs / 1.2                   # height for GUI window


# calculate x and y coordinates for GUI window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set dimensions of screen and where to place
GUI.geometry('%dx%d+%d+%d' % (w, h, x, y))

# give GUI window a title
GUI.title('Energy Control')

# Adding a menu bar
menubar = Menu(GUI)

# Adding File Menu and commands
file = Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='File', menu = file)
file.add_command(label ='New File', command = None)
file.add_command(label ='Open...', command = None)
file.add_command(label ='Save', command = None)
file.add_separator()
file.add_command(label ='Exit', command = GUI.destroy, accelerator="Ctrl+Q")
GUI.config(menu = menubar)

# Adding Info menu and commands
info = Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='Info', menu = info)
info.add_command(label ='About', command = show_info_about_message)

GUI.config(menu = menubar)

# act on keyboard key press, by associating key press event with a function 
GUI.bind('<KeyPress>', onKeyPress)

# create a label in GUI window as title for LOWI data to display, by calling self-defined GUI_label_widget() function 
LOWI_label = GUI_label_widget('Electrical Meter - LOWI - 2-Wire')

# create a text widget in GUI window, by calling self-defined GUI_text_widget_LOWI() function 
LOWI_text_display_window = GUI_text_widget_LOWI('Electrical Meter - LOWI', 160, 26)
print_text_mask_GUI_LOWI()

# create a label in GUI window as title for LOWI data to display, by calling self-defined GUI_label_widget() function 
PLUG_label = GUI_label_widget('Smart Plug - 2-Wire')


# create a text widget in GUI window, by calling self-defined GUI_text_widget() function 
PLUG_text_display_window = GUI_text_widget_PLUG('Smart Plug', 160, 15)


#connecting with new instance to MQTT server for reading LOWI meter info
PLUG_Connected_read = False                                     #global variable for state of connection; set to False = not connected
client_LOWI_read = mqttClient.Client("Qonnex_LOWI_read")        #create read new LOWI MQTT client instance
client_LOWI_read.username_pw_set(MQTT_TOKEN, MQTT_PW)           #set user name and password
client_LOWI_read.on_connect = LOWI_on_connect_read              #attach read function to callback
client_LOWI_read.connect(MQTT_BROKER)                           #connect to MQTT broker / server
client_LOWI_read.on_message = LOWI_on_message                   #associate / link (not 'call'!) LOWI_on_message function with on_message function of LOWI MQTT client instance
client_LOWI_read.loop_start()                                   #start plug reading loop

# connecting with new instance to MQTT server for  reading PLUG meter info
client_PLUG_read = mqttClient.Client("Qonnex_plug_read")        #create read new PLUG MQQT read instance
client_PLUG_read.username_pw_set(MQTT_TOKEN, MQTT_PW)           #se1010101010t user name and password
client_PLUG_read.on_connect = PLUG_on_connect_read              #attach read function to callback
client_PLUG_read.connect(MQTT_BROKER)                           #connect to MQTT broker / server
client_PLUG_read.loop_start()                                   #start plug reading loop
while PLUG_Connected_read != True:                              #Wait for plug read connection
    time.sleep(0.1) 
client_PLUG_read.on_message = PLUG_on_message_read      

# connecting with new instance to MQTT server for writing / switching PLUG 
PLUG_Connected_write = False                                    #global variable for state of connection; set to False = not connected
client_PLUG_write = mqttClient.Client("Qonnex_plug_write")      #create write new instance
client_PLUG_write.username_pw_set(MQTT_TOKEN, MQTT_PW)          #set user name and password
client_PLUG_write.on_connect = PLUG_on_connect_write            #attach write function to callback
client_PLUG_write.connect(MQTT_BROKER)                          #connect to broker
client_PLUG_write.loop_start()                                  #start plug writing loop
while PLUG_Connected_write != True:                             #Wait for plug write connection to be confirmed
    time.sleep(0.2) 
client_PLUG_write.publish(PLUG_TOPIC_WRITE,"OFF")

# launch function in separate thread (to not block GUI) with (endless) loop to scan for user's keyboard key press
#Process = threading.Thread(target=run_loop)                     #launch function in different thread, in order to not block for GUI window
#eeProcess.start()

# run GUI endless loop()
GUI.mainloop()

# when / once the GUI is getting closed / exited
client_PLUG_read.disconnect()                                #disconnect read connection
client_PLUG_read.loop_stop()                                 #end read loop
client_PLUG_write.disconnect()                               #disconnect read connection
client_PLUG_write.loop_stop()                                #end write loop
client_LOWI_read.disconnect()
client_LOWI_read.loop_stop()
clear_console() 
sys.exit()

        
