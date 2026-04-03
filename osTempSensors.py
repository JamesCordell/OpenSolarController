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
import settings
import numbers
from openSolarDb import Db
from w1thermsensor import W1ThermSensor, Sensor


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def initSerial(serialNum):
  if serialNum == 0:
    try:
        return serial.Serial(port=settings.arduinoSerialDev0,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)
    except:
        eprint("Serial Error dev0: " + str(sys.exc_info()[0]))
  if serialNum == 1:
    try:
        return serial.Serial(port=settings.arduinoSerialDev1,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)
    except:
        eprint("Serial Error: Dev1" + str(sys.exc_info()[0]))

def getMAX(sensorsData,dev):
  try:
    dev.write(b'\n') #  arduino code expects a carrier return to initiate sending 1 packet of data.
  except AttributeError:
      eprint("Error writing to Arduino.")
      return
  try:
    dev.readline()
  except serial.serialutil.SerialException:
    eprint("serial error")
  jsonStr = dev.readline().decode("utf-8")
  if jsonStr: # if data
    try:
      temp = json.loads(jsonStr)
      for k,v in temp.items():
        if v != "":
          sensorsData[k] = float(v)

      assert(temp['f1'] == "")
      assert(temp['f2'] == "")
    except:
      eprint("Fault from Arduino json string:" + jsonStr)
      eprint("Error: " + str(sys.exc_info()[0]))

def truncate(x):
  return float(int(x * 10) / 10)

if __name__ == '__main__':
    db = Db()
    sensorsData0 = dict()
    sensorsData1 = dict()
    sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=settings.ds18b20_1)
    while True:
#      dev0 = initSerial(0)
      dev1 = initSerial(1)
#      if dev0 is not None:
#        getMAX(sensorsData0, dev0)
      if dev1 is not None:
        getMAX(sensorsData1, dev1)
#      else:
      sensorsData0['t1'] = 0
      sensorsData0['t2'] = float(truncate(sensor.get_temperature()))

      dev1 = initSerial(1)
        
      db.logINSERT(sensorsData0)
      db.logINSERT(sensorsData1)
      db.statusUPDATE(sensorsData0,'sensorId')
      db.statusUPDATE(sensorsData1,'sensorId')
      time.sleep(1)
