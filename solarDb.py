
import sqlite3
from sqlite3 import Error
import time

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
    return self.cur.fetchmany(24 * 60 * 60)

  def logINSERT(self,itemId,value): #  Dirivative compression. If the temperature changes beyond a limit or a minimum ammount of time log temperature.
    self.cur.execute('SELECT value,time FROM log WHERE itemId=' + str(itemId) + ' order by time desc')
    valueDb = float(self.cur.fetchone()[0])
    epoch = int(self.cur.fetchone()[1])
    print(str(epoch - int(time.time())))
    print(str(valueDb) + " " + str(value))
    if (float(value) > (valueDb + 1) or float(value) < (valueDb - 1)) or int(time.time() - 300) > epoch: # if temp change is bigger than one degree log temp.
        self.query('INSERT INTO log (time,itemId,value) VALUES (' + str(int(time.time())) + ',' + str(itemId) + ',' + str(value) + ')')
   
  def statusUPDATE(self,itemName,value):
    self.query('UPDATE status SET value=' + value + ' WHERE "key"="' + itemName + '"')

  def getValue(self,q):
    self.cur.execute("SELECT value FROM status WHERE key='" + q + "'")
    return str(self.cur.fetchone()[0])

