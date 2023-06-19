
import time
import settings
import math
import sys
from sqlalchemy import create_engine
from sqlalchemy import text

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Db:
  engine = None
  conn = None
  cur = None
  
  def __init__(self):
    """ create a database connection to a SQLite database """
    url = "mariadb+mariadbconnector://" + settings.dbUser + ":" + settings.dbPassword + "@" + settings.dbHost + "/" + settings.dbName #?charset=utf8mb4'

    self.engine = create_engine(url, echo=True)

  def query(self,q):
    res = self.engine.execute(text(q))
    return res

  def getLog(self,sensorName):
    self.cur.execute("SELECT time,CAST(value AS INT) FROM `log` WHERE `Id`=(select `Id` from `status` where `status`.`name`='" + str(sensorName) + "') order by time desc")
    return self.cur.fetchmany(24 * 60 * 60)

  def logINSERT(self,sensorsData): #  Dirivative compression. If the temperature changes beyond a limit or a minimum ammount of time log temperature.
    if not sensorsData:
      return
    for sensorId,value in sensorsData.items():
      if sensorId[0:1] == 't':
        res = self.query("SELECT value,time from `openSolar`.`log` where `sensorId`='" + str(sensorId) + "' order by time desc limit 1").first()
        if res[0] is not None:
          valueDB = float(res[0]) 
          epochTimeDB = int(res[1])
          print(str(sensorId))
          print(str(int(time.time()) - 120) + " " + str(epochTimeDB))
          print(int(time.time()) - 120 > epochTimeDB)
          #if int(valueDB) > 140: # Don't log temperatures above this. This must be an error.
          #    continue
          if (not math.isclose(value, valueDB, abs_tol=1)) or (int(time.time() - 600) > epochTimeDB): # if temp change is bigger than one degree log temp.
            self.query("INSERT INTO log (`sensorId`,`time`,`value`) VALUES ('" + str(sensorId) + "','" + str(int(time.time())) + "','" + str(value) + "')")
   
  def statusUPDATE(self,sensorsData,field):
    for sensorId,value in sensorsData.items():
      self.query("UPDATE status SET value=" + str(value) + " WHERE `" + field + "`='" + sensorId + "'" )

  def getStatusValueViaName(self,name):
    self.query("SELECT value FROM status WHERE `name`='" + name + "'")
    return str(self.cur.fetchone()[0])

  def getStatusIntValueViaName(self,name):
    self.query("SELECT CAST(value AS int) FROM status WHERE `name`='" + name + "'")
    return str(self.cur.fetchone()[0])

