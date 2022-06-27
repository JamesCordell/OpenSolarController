
import sqlite3
from sqlite3 import Error
import mysql.connector
import time
import settings

class Db:
  conn = None
  cur = None
  
  def __init__(self,db_file):
    """ create a database connection to a SQLite database """
    try:
      #self.conn = sqlite3.connect(db_file, isolation_level=None)
      self.conn = mysql.connector.connect(user=settings.dbUser,password=settings.dbPassword, database=settings.dbName,host=settings.dbHost,buffered=True)
      self.conn.autocommit = True
      self.cur = self.conn.cursor()
    except Error as e:
      print(e)
    finally:
      if not self.conn:
        self.conn.close()
        eprint('Closing db')

  def __del__(self):
    self.cur.close()
    self.conn.close()

  def query(self,q):
    self.cur.execute(q)
    return self.cur.fetchmany(24 * 60 * 60)

  def getLog(self,sensorName):
    self.cur.execute("SELECT time,CAST(value AS INT) FROM `log` WHERE `Id`=(select `Id` from `status` where `status`.`name`='" + str(sensorName) + "') order by time desc")
    return self.cur.fetchmany(24 * 60 * 60)

  def logINSERT(self,sensorsData): #  Dirivative compression. If the temperature changes beyond a limit or a minimum ammount of time log temperature.
    for sensorId,value in sensorsData.items():
      print(sensorId,value)
      self.cur.execute("SELECT sensorId,value,time from `openSolar`.`status` where `sensorId`='" + str(sensorId) + "' order by time desc")
      res =  self.cur.fetchone()
      if res is not None:
        Id = str(res[0])
        value = float(res[1])
        epochTime = int(res[2])
        #print(str(valueDb) + " " + str(value))
        if (float(value) > (value + 1) or float(value) < (value - 1)) or int(time.time() - 300) > epochTime: # if temp change is bigger than one degree log temp.
          self.query("INSERT INTO log (`sensorId`,`time`,`value`) VALUES ('" + str(Id) + "','" + epochTime + "','" + str(value) + "')")
      else:
        print("first log entry")
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

