
#Create the database
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

timeZone             = "Europe/London"
arduinoSerialDev0    = '/dev/ttyUSB0'
arduinoSerialDev1    = '/dev/ttyUSB1'
dpsSerialDev0        = '/dev/ttyUSB2'
ifName               = 'eth0'
ifNameFallback       = 'wlan0'
dbFile               = 'OpenSolar.db'
dbUser               = 'openSolar'
dbPassword           = 'openSolar'
dbName               = 'openSolar'
dbHost               = '127.0.0.1'
