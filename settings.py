
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
#arduinoSerialDev0    = '/dev/serial/by-path/platform-5311400.usb-usb-0:1:1.0-port0'
#arduinoSerialDev1    = '/dev/serial/by-path/platform-xhci-hcd.1.auto-usb-0:1:1.0-port0'
dpsSerialDev0        = '/dev/serial/by-path/platform-5101400.usb-usb-0:1:1.0-port0'
ds18b20_1            = '00000036061c'
ifName               = 'eth0'
ifNameFallback       = 'wlan0'
dbFile               = 'OpenSolar.db'
dbUser               = 'openSolar'
dbPassword           = 'openSolar'
dbName               = 'openSolar'
dbHost               = '127.0.0.1'
