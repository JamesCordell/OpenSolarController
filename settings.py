
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
arduinoSerialDev0    = '/dev/serial/by-path/platform-1c1a400.usb-usb-0:1:1.0-port0'
arduinoSerialDev1    = '/dev/serial/by-path/platform-1c1b400.usb-usb-0:1:1.0-port0'
dpsSerialDev0        = '/dev/serial/by-path/platform-1c1d400.usb-usb-0:1:1.0-port0'
ifName               = 'eth0'
ifNameFallback       = 'wlp3s0'
dbFile               = 'OpenSolar.db'
dbUser               = 'openSolar'
dbPassword           = 'openSolar'
dbName               = 'openSolar'
dbHost               = '127.0.0.1'
