
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
arduinoSerialDev     = '/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0'
ifName               = 'wlan0'
ifNameFallback       = 'wlp3s0'
dbFile               = 'OpenSolar.db'
dbUser               = 'openSolar'
dbPassword           = 'openSolar'
dbName               = 'openSolar'
dbHost               = '127.0.0.1'
