import sqlite3
from sqlite3 import Error
from datetime import datetime
import pytz
import time

from w1thermsensor import W1ThermSensor
try:
  sensor = W1ThermSensor()
except KernelModuleLoadError as e:
  print(e)

while True:
  temp1 = sensor.get_temperature()
  temp2 = sensor.get_temperature()
  temp3 = sensor.get_temperature()
  print("The temperature is %s celsius" % ((temp1 + temp2 + temp3) / 3))
  time.sleep(1)

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
      print(e)
    finally:
      if not self.conn:
        self.conn.close()
        print('Closing db')
          
  def __del__(self):
    self.conn.commit()
    self.cur.close()
    self.conn.close()

  def query(self,q):
    self.cur.execute(q)
   
if __name__ == '__main__':
    db = Db('OpenSolar.db')
    avgTemp = (sensor.get_temperature() + sensor.get_temperature() + sensor.get_temperature()) / 3
    print("INSERT INTO log (time,itemId,value) VALUES ("+str(int(time.time()))+",1,"+avgTemp+")")
    print(db.query('INSERT INTO log (time,itemId,value) VALUES ('+str(int(time.time()))+',1,'+avgTemp+')'))
