from __future__ import print_function
import sqlite3
from sqlite3 import Error
from datetime import datetime
import pytz
import time
import serial
import binascii
import json
import sys
import serial
import statistics
from w1thermsensor import W1ThermSensor, SensorNotReadyError, NoSensorFoundError
import settings  #User defined

from solarDb import Db

tX = dict()
tX[settings.tankBottomTempDSID] = "t3"
tX[settings.tankTopTempDSID] = "t4"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

try:
  sensor = W1ThermSensor()
except KernelModuleLoadError as e:
  eprint("Error: " + e)

def truncate(x):
  return float(int(x * 10) / 10)

def getDS18b20(sensorsData):
  for s in W1ThermSensor.get_available_sensors():
    avgTemp=[]
    for i in range(3):
      try:
        avgTemp.append(W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20,s.id).get_temperature())
        time.sleep(1)
      except SensorNotReadyError or NoSensorFoundError:
        pass
    try:
      sensorsData[ tX[s.id] ] = truncate(statistics.mode(avgTemp)) #  Translate DS18b20 to tX for simplicity
    except statistics.StatisticsError:
      pass
    time.sleep(1)

def getMAX(sensorsData):
  dev.write(b'\n') #  arduino code expects a carrier return to initiate sending 1 packet of data.
  jsonStr = dev.readline().decode("utf-8")  #  decode two bytes and remove \n
  if jsonStr: #  is string not empty
    try:
      temp = json.loads(jsonStr)
      sensorsData["t1"] = float(temp["t1"])
      sensorsData["t2"] = float(temp["t2"])
    except:
      eprint("Error: " + str(sys.exc_info()[0]))

if __name__ == '__main__':
    db = Db(settings.dbFile)
    try:
      dev = serial.Serial(settings.arduinoSerialDev,
      baudrate=115200,
      bytesize=serial.EIGHTBITS,
      parity=serial.PARITY_EVEN,
      stopbits=serial.STOPBITS_ONE,
      timeout=1)
    except:
      pass

    while True:
      sensorsData = dict()
      getDS18b20(sensorsData)
      #getMAX(sensorsData)
      print( sensorsData )
      try:
        db.logINSERT(4,sensorsData["t4"])
        db.statusUPDATE('tankBottomTemp',sensorsData["t4"])
      except:
        pass
      if len(sensorsData) >= 4:
        print( sensorsData )
        db.logINSERT(1,sensorsData["t1"])
        db.statusUPDATE('collInTemp',sensorsData["t1"])
        db.logINSERT(2,sensorsData["t2"])
        db.statusUPDATE('collOutTemp',sensorsData["t2"])
        db.logINSERT(3,sensorsData["t3"])
        db.statusUPDATE('tankBottomTemp',sensorsData["t3"])
        db.logINSERT(4,sensorsData["t4"])
        db.statusUPDATE('tankTopTemp',sensorsData["t4"]) 
      time.sleep(1)
