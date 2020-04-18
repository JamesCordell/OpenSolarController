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

from openSolarDb import Db

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

try:
  sensor = W1ThermSensor()
except KernelModuleLoadError as e:
  eprint("Error: " + e)

def truncate(x):
  return float(int(x * 10) / 10)

def getDS18b20(sensorsData):
  for W1SensorID in W1ThermSensor.get_available_sensors():
    avgTemp=[]
    for i in range(3):
      try:
        avgTemp.append(W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20,W1SensorID.id).get_temperature())
        time.sleep(1)
      except SensorNotReadyError or NoSensorFoundError:
        pass
    try:
      sensorsData[ W1SensorID.id ] = truncate(statistics.mode(avgTemp)) #  Translate DS18b20 to ID for simplicity
    except statistics.StatisticsError:
      pass
    time.sleep(1)

def getMAX(sensorsData):
  dev.write(b'\n') #  arduino code expects a carrier return to initiate sending 1 packet of data.
  jsonStr = dev.readline().decode("utf-8")  #  decode two bytes and remove \n
  if jsonStr: #  is string not empty
    try:
      temp = json.loads(jsonStr)
      sensorsData[settings.collInTempID]  = float(temp[settings.collInTempID])
      sensorsData[settings.collOutTempID] = float(temp[settings.collOutTempID])
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
      getMAX(sensorsData)
      try:
        db.logINSERT(sensorsData)
        db.statusUPDATE(sensorsData)
      except:
        pass
      print( sensorsData )
      db.logINSERT(sensorsData)
      db.statusUPDATE(sensorsData)
      time.sleep(1)
