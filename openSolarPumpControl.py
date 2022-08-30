import pydps,time
import settings
import time
# dps Test Example
dps = pydps.dps_psu(settings.dpsSerialDev0, 1) # port name, slave address (in decimal)

from openSolarDb import Db


def main():

    db = Db(settings.dbFile)
    rowPrev = dict()
    # example data {'u-set': 8.8, 'i-set': 1.0, 'u-out': 8.72, 'i-out': 0.428, 'power': 3.73, 'u-in': 15.11, 'lock': 0, 'protect': 0, 'cvcc': 1, 'on': 1, 'b-led': 4, 'model': 5005, 'fw-version': '1.4', 's-ovp': 51.0, 's-ocp': 5.2, 's-opp': 2652}
    #Read only data
    fullData = dps.getFullData()
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'u-out'," + str(fullData['u-out']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'i-out'," + str(fullData['i-out']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'power'," + str(fullData['power']) + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'u-in' ," + str(fullData['u-in'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'cvcc' ," + str(fullData['cvcc'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'model' ," + str(fullData['model'])  + ")")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'fw-version' ," + str(fullData['fw-version'])  + ")")
      
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control1-p' ,0)")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control2-i' ,0)")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control3-d' ,0)")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control4-t' ,0)")
    db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'control5-t' ,0)")

    while(True):
      fullData = dps.getFullData()
      db.query("UPDATE status SET value=" + str(fullData['u-out']) + ",time=" + str(time.time()) +" WHERE sensorId='u-out'")
      db.query("UPDATE status SET value=" + str(fullData['i-out']) + " WHERE sensorId='i-out'")
      db.query("UPDATE status SET value=" + str(fullData['power']) + " WHERE sensorId='power'")
      db.query("UPDATE status SET value=" + str(fullData['u-in'])  + " WHERE sensorId='u-in'")
      db.query("UPDATE status SET value=" + str(fullData['cvcc'])  + " WHERE sensorId='cvcc'")
      db.query("UPDATE status SET value=" + str(fullData['model'])  + " WHERE sensorId='model'")
      db.query("UPDATE status SET value=" + str(fullData['fw-version'])  + " WHERE sensorId='fw-version'")
    
      #Read and write data
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'u-set'," + str(fullData['u-set']) + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'i-set'," + str(fullData['i-set']) + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'lock' ," + str(fullData['lock'])  + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'protect' ," + str(fullData['protect'])  + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 'on' ," + str(fullData['on'])  + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 's-ovp' ," + str(fullData['s-ovp'])  + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 's-ocp' ," + str(fullData['s-ocp'])  + ")")
      db.query("INSERT IGNORE INTO status (`sensorId`,`value`) VALUE ( 's-opp' ," + str(fullData['s-opp'])  + ")")
 
      db.cur = db.conn.cursor(dictionary=True)
      ret = db.query("SELECT * FROM status WHERE sensorId IN('u-set','i-set','lock','on','s-ovp','s-ocp','s-opp')") 
      for row in ret:
        try:
          if float(row['value']) != float(rowPrev[row['sensorId']]):
            dps.setById(row['sensorId'],float(row['value']))
          rowPrev[row['sensorId']] = float(row['value'])
        except KeyError:
          rowPrev[row['sensorId']] = float(row['value'])

      # Sets the proportion of pump rate. 
      db.query("""
UPDATE openSolar.status SET value=
	(SELECT 
	CASE
	WHEN
		(SELECT 
	 	CASE
		WHEN 
			(select
				(
				(SELECT value FROM openSolar.status WHERE sensorId='t4') -  -- sample
				(SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2')) -- error
				)
			* (SELECT value FROM openSolar.status WHERE sensorId='control1-p') -- gain
			AS 'p')
			< 0
		THEN 0
		ELSE
			(SELECT
			CASE
			WHEN
				(select
					(
					(SELECT value FROM openSolar.status WHERE sensorId='t4') -  -- sample
					(SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2')) -- error
					)
				* (SELECT value FROM openSolar.status WHERE sensorId='control1-p') -- gain
				AS 'p')
				> 11
			THEN 11
			ELSE
				(select
					(
					(SELECT value FROM openSolar.status WHERE sensorId='t4') -  -- sample
					(SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2')) -- error
					)
				* (SELECT value FROM openSolar.status WHERE sensorId='control1-p') -- gain
				AS 'p')
			END AS 'below 12')
		END AS 'above 0')
		> 7.8
		THEN
			(SELECT 
		 	CASE
			WHEN 
				(select
					(
					(SELECT value FROM openSolar.status WHERE sensorId='t4') -  -- sample
					(SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2')) -- error
					)
				* (SELECT value FROM openSolar.status WHERE sensorId='control1-p') -- gain
				AS 'p')
				< 0
			THEN 0
			ELSE
				(SELECT
				CASE
				WHEN
					(select
						(
						(SELECT value FROM openSolar.status WHERE sensorId='t4') -  -- sample
						(SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2')) -- error
						)
					* (SELECT value FROM openSolar.status WHERE sensorId='control1-p') -- gain
					AS 'p')
					> 11
				THEN 11.5
				ELSE
					(select
						(
						(SELECT value FROM openSolar.status WHERE sensorId='t4') -  -- sample
						(SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2')) -- error
						)
					* (SELECT value FROM openSolar.status WHERE sensorId='control1-p') -- gain
					AS 'p')
				END AS 'below 12')
			END AS 'above 0')
		ELSE 0
		END AS 'above 7.8')
WHERE sensorId ='u-set' """)
      # Turns pump on and off.
      db.query(""" 
            UPDATE openSolar.status SET value=(
	            SELECT
	                CASE
	                    WHEN 
                          (SELECT
                            CASE
                            WHEN (SELECT value from openSolar.status where sensorId='on')
                            = 0
                            THEN (SELECT value    from openSolar.status where sensorId='t4')
                            ELSE (SELECT value + (SELECT value FROM openSolar.status WHERE sensorId='control5-t') from openSolar.status where sensorId='t4')
                          END AS 'temp')
	                    >
	                    (SELECT avg(value) + (SELECT value FROM openSolar.status WHERE sensorId='control4-t') AS 'control4-t' FROM openSolar.status WHERE sensorId IN('t1','t2'))
	                    THEN 1
	                    ELSE 0
	                END AS 'onoff')
                WHERE sensorId='on'
              """)

if __name__ == "__main__":
    main()
