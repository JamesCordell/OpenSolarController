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
from statistics import mean 

arduinoSerialDev = '/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0'
dbFile = 'OpenSolar.db'

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#from w1thermsensor import W1ThermSensor
#try:
#  sensor = W1ThermSensor()
#except KernelModuleLoadError as e:
#  print(e)

#CREATE TABLE log (
	#time INTEGER DEFAULT 0 NOT NULL,
	#itemId INTEGER DEFAULT 0 NOT NULL,
	#value NUMERIC DEFAULT 0 NOT NULL
#);

#CREATE INDEX log_time_IDX ON log (time,itemId);


#CREATE TABLE status (
	#"key" TEXT(255),
	#value INTEGER
#);

class Db:
  conn = None
  cur = None
  def __init__(self,db_file):
    """ create a database connection to a SQLite database """
    try:
      self.conn = sqlite3.connect(db_file, isolation_level=None)
      self.cur = self.conn.cursor()
    except Error as e:
      eprint(e)
    finally:
      if not self.conn:
        self.conn.close()
        eprint('Closing db')

  def __del__(self):
    self.conn.commit()
    self.cur.close()
    self.conn.close()

  def query(self,q):
    self.cur.execute(q)
    
  def logINSERT(self,itemId,value):
    self.query('INSERT INTO log (time,itemId,value) VALUES (' + str(int(time.time())) + ',' + str(itemId) + ',' + str(value) + ')')
   
  def statusUPDATE(self,itemName,value):
    self.query('UPDATE status SET value=' + value + ' WHERE "key"="' + itemName + '"')

if __name__ == '__main__':
    db = Db(dbFile)
    dev = serial.Serial(arduinoSerialDev,
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=1)

    while True:
      dev.write(b'\n') #  arduino code expects a carrier return to initiate sending 1 packet of data.
      temperature = dict()
      jsonStr = dev.readline().decode("utf-8")  #  decode two bytes and remove \n
      if jsonStr: #  is string not empty
        try:
          temperature = json.loads(jsonStr)
        except:
          eprint("Error: " + str(sys.exc_info()[0]))

      #temp[0] = sensor.get_temperature()
      #temp[1] = sensor.get_temperature()
      #temp[2] = sensor.get_temperature()
      #avgTemp = (sensor.get_temperature() + sensor.get_temperature() + sensor.get_temperature()) / 3
      #print("INSERT INTO log (time,itemId,value) VALUES ("+str(time.time())+",1,"+avgTemp+")")
        db.logINSERT(1,temperature["t1"])
        db.statusUPDATE('collInTemp',temperature["t1"])
        db.logINSERT(2,temperature["t2"])
        db.statusUPDATE('collOutTemp',temperature["t2"])
      time.sleep(1)
