#
# coding=utf-8
# Plugin: Fuel Consumption plugin
# Developer: Tristan Israël - Alefbet
#
"""
<plugin key="FuelConsumption" name="Fuel Consumption" author="alefbet" version="1.0.4" wikilink="" externallink="https://alefbet.net/">
    <description>
        <h2>Noise Alarm</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>A remplir</li>            
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>A remplir</li>            
        </ul>
    </description>
    <params>      
        <param field="Mode1" label="Nozzle flow (L/h)" width="200px" required="true" default="2.4"/>        
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import sys
import math
import audioop
import socket
import io
import os
import time
import json
from datetime import datetime
import Domoticz

class BasePlugin:    
    lastUpdate = 0     
    isOn = False # Flame is On?    
    isReady = False
    jsonData = {}
    
    def createDevices(self):
        if not 1 in Devices:
            Domoticz.Device(Name="Burner state",  Unit=1, Type=244, Subtype=62, Switchtype=0, Used=1).Create()            
            Domoticz.Log("Created device " + Devices[1].Name)
            if not 1 in Devices:
                Domoticz.Log("Device could not be created")
                return False   
        
        if not 2 in Devices:
            Domoticz.Device(Name="Current", Unit=2, TypeName="Custom", Options={"Custom": "1.0;L"}, Used=1).Create()           
            Domoticz.Log("Created device " + Devices[2].Name)
            if not 2 in Devices:
                Domoticz.Log("Device could not be created")
                return False

        if not 3 in Devices:
            Domoticz.Device(Name="Total", Unit=3, TypeName="Custom", Options={"Custom": "1.0;L"}, Used=1).Create()           
            Domoticz.Log("Created device " + Devices[3].Name)
            if not 3 in Devices:
                Domoticz.Log("Device could not be created")
                return False  
                
        if not 4 in Devices:
            Domoticz.Device(Name="Today", Unit=4, TypeName="Custom", Options={"Custom": "1.0;L"}, Used=1).Create()           
            Domoticz.Log("Created device " + Devices[4].Name)
            if not 4 in Devices:
                Domoticz.Log("Device could not be created")
                return False      

        return True

    def dbFilepath(self):
        filedir = os.path.dirname(os.path.realpath(__file__))
        return filedir +'/fuel_consumption.json'

    def readDb(self):
        try:
            with open(self.dbFilepath(), 'r') as f:                
                self.jsonData = json.load(f)  
                return True                  
        except:
            return False
            
        return False

    def initDb(self):
        with open(self.dbFilepath(), 'w+') as f:
            try:
                json.load(f)
                return True
            except(json.decoder.JSONDecodeError):
                Domoticz.Debug("Initialize db file")
                self.jsonData = {"today": 0.0, "total": 0.0, "current_date": "1970-01-01", "total_duration": 0}
                json.dump(self.jsonData, f)
                return True

        return False

    def updateDb(self):
        try:
            with open(self.dbFilepath(), 'w') as f:        
                json.dump(self.jsonData, f)
                self.lastUpdate = datetime.now()
                return True
        except:              
            return False                

        return False        

    def verifyDayChanged(self):
        # Check if day changed
        last_current_date_str = self.lastDbValue("current_date")
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        if last_current_date_str != current_date_str:
            self.jsonData["today"] = 0.0
            self.jsonData["current_date"] = current_date_str
            self.updateDb()
            Devices[4].Update(nValue=0, sValue="0")

    def lastDbValue(self, counter):
        with open(self.dbFilepath(), 'r') as f:
            try:
                jsonData = json.load(f)
                return jsonData[counter]
            except:
                Domoticz.Log("Impossible to read fuel_consumption.json file")  

    def onStart(self):        
        # Check Debug setting
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()
               
        if self.createDevices():
            self.isReady = True
        else:
            return 

        if not self.readDb():
            Domoticz.Debug("Could not read database file. Try to initialize it.")
            if self.initDb():                
                self.isReady = True
            else:
                Domoticz.Log("Could not initialize database file. Abort.")
                return

        self.isOn = False
        Domoticz.Debug(json.dumps(self.jsonData))

        # Init variables and counters
        Devices[2].Update(nValue=0, sValue="0")            
        Devices[3].Update(nValue=0, sValue=str(self.jsonData["total"]))
        Devices[4].Update(nValue=0, sValue="0")

        self.verifyDayChanged()

        Domoticz.Debug("Initialization done")
            
    def updateCounters(self):
        if not self.isOn:
            return        

        # Duration since last update
        duration_secs = round(datetime.timestamp(datetime.now()) - datetime.timestamp(self.lastUpdate))
        if duration_secs == 0:
            return
            
        Domoticz.Debug("Flame has been On during " +str(duration_secs) +" seconds since last update")            

        # Calculate cumulated consumption
        lastValue = self.jsonData["total"]
        newValue = float(lastValue) + self.consumptionInLiters(duration_secs)
        self.jsonData["total"] = newValue                

        # Calculate today's consumption
        last_current_date_str = self.lastDbValue("current_date")
        #last_current_date = datetime.strptime(last_current_date_str, '%Y-%m-%d')
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        if last_current_date_str == current_date_str:
            lastValue = self.jsonData["today"]
            newValue = float(lastValue) + self.consumptionInLiters(duration_secs)
            self.jsonData["today"] = newValue
        else:
            #self.jsonData["today"] = self.consumptionInLiters(duration_secs)
            self.jsonData["today"] = 0.0
            self.jsonData["current_date"] = current_date_str

        # Calculate total duration
        lastValue = self.jsonData["total_duration"]
        newValue = int(lastValue) + duration_secs
        self.jsonData["total_duration"] = newValue

        # Update devices
        Devices[3].Update(nValue=0, sValue=str(self.jsonData["total"]))
        Devices[4].Update(nValue=0, sValue=str(self.jsonData["today"]))                         

        # Update db
        self.updateDb()        

    def onStop(self):
        Domoticz.Debug("onStop called")                     
        self.isStarted = False

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        
    def onMessage(self, Data, Status, Extra):
        Domoticz.Debug("onMessage called: Data=" +str(Data))

    def consumptionInLiters(self, duration_in_secs):
        s_in_hour = 1/3600
        flow_per_hour = float(Parameters["Mode1"]) #L/h
        flow_per_second = flow_per_hour*s_in_hour
        consumption = duration_in_secs*flow_per_second
        return round(consumption, 3)

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called: Unit=" +str(Unit))
        if Unit == 1:
            if Command == "On":
                Devices[1].Update(nValue=1, sValue="On")
                Domoticz.Debug("Flame is On")
                self.lastUpdate = datetime.now()  
                self.isOn = True              
            if Command == "Off":
                Devices[1].Update(nValue=0, sValue="Off")                
                Domoticz.Debug("Flame is Off")                

                # Reset current consumption
                Devices[2].Update(nValue=0, sValue="0")  

                self.updateCounters()         
                self.isOn = False      

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        self.isAlive = True
        
        # Calculate current consumption (since On)        
        if self.isOn:
            duration_secs = round(datetime.timestamp(datetime.now()) - datetime.timestamp(self.lastUpdate))
            Domoticz.Debug("Heartbeat: Flame has been On during " +str(duration_secs) +" seconds since last update") 
            consumption = self.consumptionInLiters(duration_secs)
            Devices[2].Update(nValue=0, sValue=str(consumption))
        else:            
            Devices[2].Update(nValue=0, sValue="0")            
            self.verifyDayChanged()

        # Update db
        self.updateCounters()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return