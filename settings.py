
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
dbFile               = "OpenSolar.db"
arduinoSerialDev     = '/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0'
ifName               = 'wlp3s0'
tankBottomTempDSID   = '020a92454e33'
tankTopTempDSID      = '021792453daa'
dbUser               = 'openSolar'
dbPassword           = 'openSolar'
dbName               = 'openSolar'
dbHost               = '127.0.0.1'

