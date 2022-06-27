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

from openSolarDb import Db

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def truncate(x):
  return float(int(x * 10) / 10)

def getMAX(sensorsData,dev):
  try:
    dev.write(b'\n') #  arduino code expects a carrier return to initiate sending 1 packet of data.
  except AttributeError:
      return
  jsonStr = dev.readline().decode("utf-8")  #  decode two bytes and remove \n
  if jsonStr: #  is string not empty
    try:
      temp = json.loads(jsonStr)
      sensorsData['t1'] = float(temp['t1'])
      sensorsData['t2'] = float(temp['t2'])
    except:
      eprint("Fault from Arduino f1:" + sensorsData["f1"] + " f2:" + sensorsData["f2"])
      eprint("Error: " + str(sys.exc_info()[0]))
  sensorsData = dict()

def initSerial(serialNum):
  if serialNum == 0:
    try:
        return serial.Serial(settings.arduinoSerialDev0,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)
    except:
        eprint("Serial Error: " + str(sys.exc_info()[0]))
  if serialNum == 1:
    try:
        return serial.Serial(settings.arduinoSerialDev1,
        #baudrate=115200,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)
    except:
        eprint("Serial Error: " + str(sys.exc_info()[0]))

if __name__ == '__main__':
    db = Db(settings.dbFile)
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
      db.statusUPDATE(sensorsData0,'sensorId')
      db.statusUPDATE(sensorsData1,'sensorId')
      db.logINSERT(sensorsData0)
      db.logINSERT(sensorsData1)
      time.sleep(1)
