import pydps,time
import signal
import time
import settings
import time
import math
# dps Test Example
dps = pydps.dps_psu(settings.dpsSerialDev0, 1) # port name, slave address (in decimal)

from openSolarDb import Db

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


def main():

    db = Db()
    rowPrev = dict()
    # example data {'u-set': 8.8, 'i-set': 1.0, 'u-out': 8.72, 'i-out': 0.428, 'power': 3.73, 'u-in': 15.11, 'lock': 0, 'protect': 0, 'cvcc': 1, 'on': 1, 'b-led': 4, 'model': 5005, 'fw-version': '1.4', 's-ovp': 51.0, 's-ocp': 5.2, 's-opp': 2652}
    #Read only data
    fullData = dps.getFullData()
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'u-out'," + str(fullData['u-out']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'i-out'," + str(fullData['i-out']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'power'," + str(fullData['power']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'u-in' ," + str(fullData['u-in'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'protect' ," + str(fullData['protect'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'cvcc' ," + str(fullData['cvcc'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'model' ," + str(fullData['model'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'fw-version' ," + str(fullData['fw-version'])  + ")")
      
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control1-on2offThress' ,0)")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control1-off2onThress' ,0)")

    # Writable data items
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'u-set'," + str(fullData['u-set']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'i-set'," + str(fullData['i-set']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'lock' ," + str(fullData['lock'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'on' ," + str(fullData['on'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 's-ovp' ," + str(fullData['s-ovp'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 's-ocp' ," + str(fullData['s-ocp'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 's-opp' ," + str(fullData['s-opp'])  + ")")
 
    killer = GracefulKiller()
    while not killer.kill_now:
      fullData = dps.getFullData()
      print(fullData)

      # Read only data
      db.query("UPDATE status SET value=" + str(fullData['u-out']) + " WHERE sensorId='u-out'")
      db.query("UPDATE status SET value=" + str(fullData['i-out']) + " WHERE sensorId='i-out'")
      db.query("UPDATE status SET value=" + str(fullData['power']) + " WHERE sensorId='power'")
      db.query("UPDATE status SET value=" + str(fullData['u-in'])  + " WHERE sensorId='u-in'")
      db.query("UPDATE status SET value=" + str(fullData['protect'])  + " WHERE sensorId='protect'")
      db.query("UPDATE status SET value=" + str(fullData['cvcc'])  + " WHERE sensorId='cvcc'")

      # Special case were the device shuts down if over load parameters are reached.
      if str(fullData['protect']) == '1': 
        print("Overload protect set to 1 check s-ovp s-ocp s-opp")
        # rowPrev['on'] = float(0) # uncomment this to clear protect and try again.
        continue

      # Read and writeable data
      ret = db.query("SELECT * FROM status WHERE sensorId IN('u-set','i-set','lock','on','s-ovp','s-ocp','s-opp')") 
      for row in ret:
        try:
          if float(row['value']) != float(rowPrev[row['sensorId']]):
            dps.setById(row['sensorId'],float(row['value']))
          rowPrev[row['sensorId']] = float(row['value'])
        except KeyError:
          rowPrev[row['sensorId']] = float(row['value'])
          #dps.setById(row['sensorId'],float(row['value'])) # The device is crontrolled from the database

      ret = db.query("SELECT * FROM status WHERE sensorId IN('control0-loop-onoff','on','control1-off2onThress','control1-on2offThress','t1','t2','t3','t4')") 

      control = dict()
      for row in ret:
          control[row['sensorId']] = float(row['value'])

      if control['control0-loop-onoff']:
        if control['on'] == 0:
          if control['t4'] > control['control1-off2onThress']:
            db.query("UPDATE openSolar.status SET value=1 WHERE sensorId ='on' ")
        else:
          if control['t4'] < control['control1-on2offThress'] + control['t1']:
            db.query("UPDATE openSolar.status SET value=0 WHERE sensorId ='on' ")

if __name__ == "__main__":
    main()
