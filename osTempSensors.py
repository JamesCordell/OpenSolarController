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

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def truncate(x):
  return float(int(x * 10) / 10)

def getMAX(sensorsData,dev):
  try:
    dev.write(b'\n') #  arduino code expects a carrier return to initiate sending 1 packet of data.
  except AttributeError:
      eprint("Error writing to Arduino.")
      return
  dev.readline()
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
        eprint("Serial Error: " + str(sys.exc_info()[0]))
  if serialNum == 1:
    try:
        return serial.Serial(port=settings.arduinoSerialDev1,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)
    except:
        eprint("Serial Error: " + str(sys.exc_info()[0]))

if __name__ == '__main__':
    db = Db()
    dev = None
    sensorsData0 = dict()
    sensorsData1 = dict()
    while True:
      dev0 = initSerial(0)
      dev1 = initSerial(1)
      if dev0 is not None:
        getMAX(sensorsData0,dev0)
        getMAX(sensorsData1,dev1)
      else:
        dev0 = initSerial(0)
        dev1 = initSerial(1)
        
      print(sensorsData0)
      print(sensorsData1)
      db.logINSERT(sensorsData0)
      db.logINSERT(sensorsData1)
      db.statusUPDATE(sensorsData0,'sensorId')
      db.statusUPDATE(sensorsData1,'sensorId')
      time.sleep(1)
