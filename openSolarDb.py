
import sqlite3
from sqlite3 import Error
import mysql.connector
import time
import settings
import math
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Db:
  conn = None
  cur = None
  
  def __init__(self,db_file):
    """ create a database connection to a SQLite database """
    try:
      #self.conn = sqlite3.connect(db_file, isolation_level=None)
      self.conn = mysql.connector.connect(user=settings.dbUser,password=settings.dbPassword, database=settings.dbName,host=settings.dbHost, buffered=True)
      self.conn.autocommit = True
      self.cur = self.conn.cursor()
    except Error as e:
      eprint(e)
    finally:
      if not self.conn:
        self.conn.close()
        eprint('Closing db')

  def __del__(self):
    self.cur.close()
    self.conn.close()

  def query(self,q):
    self.cur.execute(q)
    #return self.cur.fetchmany(24 * 60 * 60)
    return self.cur

  def getLog(self,sensorName):
    self.cur.execute("SELECT time,CAST(value AS INT) FROM `log` WHERE `Id`=(select `Id` from `status` where `status`.`name`='" + str(sensorName) + "') order by time desc")
    return self.cur.fetchmany(24 * 60 * 60)

  def logINSERT(self,sensorsData): #  Dirivative compression. If the temperature changes beyond a limit or a minimum ammount of time log temperature.
    if not sensorsData:
      return
    for sensorId,value in sensorsData.items():
      self.cur.execute("SELECT count(sensorId) from `openSolar`.`log` where `sensorId`='" + str(sensorId) + "'")
      res = self.cur.fetchone()
      if int(res[0]) == 0: # If no entries in db
        self.query("INSERT INTO log (`sensorId`,`time`,`value`) VALUES ('" + str(sensorId) + "','" + str(int(time.time())) + "','" + str(value) + "')")
        break
      # Derivative compression
      self.cur.execute("SELECT value,time from `openSolar`.`log` where `sensorId`='" + str(sensorId) + "' order by time desc limit 1")
      res = self.cur.fetchone()
      if res is not None:
        valueDB = float(res[0]) 
        epochTimeDB = int(res[1])
        #eprint(str(sensorId))
        #eprint(str(int(time.time()) - 120) + " " + str(epochTimeDB))
        #eprint(int(time.time()) - 120 > epochTimeDB)
        if (not math.isclose(value, valueDB, abs_tol=1)) or (int(time.time() - 600) > epochTimeDB): # if temp change is bigger than one degree log temp.
          self.query("INSERT INTO log (`sensorId`,`time`,`value`) VALUES ('" + str(sensorId) + "','" + str(int(time.time())) + "','" + str(value) + "')")
   
  def statusUPDATE(self,sensorsData,field):
    for sensorId,value in sensorsData.items():
      self.query("UPDATE status SET value=" + str(value) + ",time=" + str(int(time.time())) + " WHERE `" + field + "`='" + sensorId + "'" )

  def getStatusValueViaName(self,name):
    self.cur.execute("SELECT value FROM status WHERE `name`='" + name + "'")
    return str(self.cur.fetchone()[0])

  def getStatusIntValueViaName(self,name):
    self.cur.execute("SELECT CAST(value AS int) FROM status WHERE `name`='" + name + "'")
    return str(self.cur.fetchone()[0])

