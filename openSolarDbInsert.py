import sqlite3
from sqlite3 import Error
from datetime import datetime
import pytz
import time


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
        print(sqlite3.version)
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
    print("INSERT INTO log (time,itemId,value) VALUES ("+str(int(time.time()))+",1,55)")
    print(db.query('INSERT INTO log (time,itemId,value) VALUES ('+str(int(time.time()))+',1,55)'))
