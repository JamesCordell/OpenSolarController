
import sqlite3
from sqlite3 import Error
import mysql.connector
import time
import settings

logId = {    settings.collInTempID       : 0,
             settings.collOutTempID      : 1,
             settings.tankTopTempDSID    : 2,
             settings.tankBottomTempDSID : 3 }

class Db:
  conn = None
  cur = None
  
  def __init__(self,db_file):
    """ create a database connection to a SQLite database """
    try:
      #self.conn = sqlite3.connect(db_file, isolation_level=None)
      self.conn = mysql.connector.connect(user=settings.dbUser,password=settings.dbPassword, database=settings.dbName,host=settings.dbHost,buffered=False)
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

  def logINSERT(self,sensorsData): #  Dirivative compression. If the temperature changes beyond a limit or a minimum ammount of time log temperature.
    for key,value in sensorsData.items():
      logNum = logId[ key ]
      self.cur.execute('SELECT value,time FROM log WHERE `key`=' + str(logNum) + ' order by time desc')
      try:
        lastValueDb = float(self.cur.fetchone()[0])
        lastTimeDb = int(self.cur.fetchone()[1])
        #print(str(epoch - int(time.time())))
        #print(str(valueDb) + " " + str(value))
        if (float(value) > (lastValueDb + 1) or float(value) < (lastValueDb - 1)) or int(time.time() - 300) > lastTimeDb: # if temp change is bigger than one degree log temp.
          self.query('INSERT INTO log (`time`,`key`,`value`) VALUES (' + str(int(time.time())) + ',' + str(logNum) + ',' + str(value) + ')')
      except TypeError:
        self.query('INSERT INTO log (`time`,`key`,`value`) VALUES (' + str(int(time.time())) + ',' + str(logNum) + ',' + str(value) + ')')
   
  def statusUPDATE(self,sensorsData):
    for key,value in sensorsData.items():
      self.query('UPDATE status SET value=' + str(value) + ' WHERE `key`="' + key + '"')

  def getValue(self,q):
    self.cur.execute("SELECT value FROM status WHERE `key`='" + q + "'")
    return str(self.cur.fetchone()[0])

  def getIntValue(self,q):
    self.cur.execute("SELECT CAST(value AS int) FROM status WHERE `key`='" + q + "'")
    return str(self.cur.fetchone()[0])

