This is a GUI application that can log temperatures from DS18b10 and MAX31865 temperature sensors and store them in a database. It's designed to display temerature readings and to be able to set a temperature. The tabs show a history that displays a graph.


On debian dependancies for ssh Xforwarded Arduino
apt install libxrender1 libxtst-dev libfontmanager libfreetype-dev libfreetype6 fontconfig

./arduino-1.8.19/arduino --board arduino:avr:nano:cpu=atmega328old  --port /dev/ttyUSB1 --upload p100_arduino_nano.ino 

By running 
openSolarDbInsert.py

periodically, such as on a cron job, this will log data to the database that will be picked up by the GUI live.

This GUI runs well on a raspberry pi with touch screen.

It is designed to be used with Evacuated Solar Tubes and monitor temperatures on the roof and in the tank. Also it will turn on and of an immersion heater to prevent legionella from developing. Research shows that water heated to 60 for two mintes will stop legionella. 

Screen shots
![screen shot](screen_shots/Screenshot%20from%202021-11-10%2020-19-37.png)

![screen shot](screen_shots/Screenshot%20from%202021-11-10%2020-20-02.png)
