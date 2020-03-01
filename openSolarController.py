from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock
import sqlite3
from sqlite3 import Error
from datetime import datetime, timezone, timedelta
import pytz
import time

import netifaces as ni

from math import sin
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.properties import ObjectProperty  
from kivy.app import App    
from kivy.uix.widget import Widget  

Builder.load_string("""

<TopBottom>:
  orientation: 'vertical'
  SolarControl:
    id: solarControl
    size_hint: 1, .9
    pos_hint: {'center_x': .5, 'center_y': .55}
    do_default_tab: False
    TabbedPanelItem:
      id: status
      text: 'Status'
      GridLayout:
        id: gridLayoutTabbedPanelItem
        cols: 2
        Label:
          text: 'Collector in Temp'
        Label:
          text:  root.solarControl.collInTemp
            
        Label:
          text: 'Collector out Temp'
        Label:
          text: root.solarControl.collOutTemp
            
        Label:
          text: 'Tank Top Temp'
        Label:
          text: root.solarControl.tankTopTemp
            
        Label:
          text: 'Tank Bottom Temp'
        Label:
          text: root.solarControl.tankBottomTemp
            
        Label:
          text: 'Heater Active'
        Label:
          text: root.solarControl.heaterActive

        Label:
          text: 'Pump Active'
        Label:
          text: root.solarControl.pumpActive

        Label:
          text: 'Heater off temp'
        GridLayout:
          cols: 2
          Label:
            text: root.solarControl.heaterOffTemp
          BoxLayout:
            orientation: 'vertical'
            Button:
              text: 'up'
              on_release: root.solarControl.tempUp()
            Button:
              text: 'down'
              on_release: root.solarControl.tempDown()
    TabbedPanelItem:
      text: 'History'
      BoxLayout:
        size_hint: 1.9  , 1
        id: history
        BoxLayout:
          orientation: 'vertical'
          Button:
            size_hint:  .05, .05 
            text: '+'
            on_release: root.solarControl.zoomIn()
          Button:
            size_hint:  .05, .05
            text: '-'
            on_release: root.solarControl.zoomOut()


    TabbedPanelItem:
      id: setup
      text: 'Setup'
      RstDocument:
        text:'\\n'.join(("This is the Open Solar Solar Controller written by James Cordell in python3","You are in the third tab."))
  GridLayout:
    id: gridTopBottom
    cols: 3
    size_hint: 1, .05
    font_size: '15sp'
    Label:
      text: root.currentTime
    Label:
      text: 
    Label:
      text: 'IP Address:' + root.ipAddr

""")

class db():
  conn = None
  cur = None
  def create_connection(self,db_file):
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

  def getValue(self,q):
    self.cur.execute("SELECT value FROM status WHERE key='" + q + "'")
    return self.cur.fetchone()[0]

  def query(self,q):
    self.cur.execute(q)
    return self.cur.fetchmany(24 * 60 * 60)

class SolarControl(TabbedPanel):
  
  collInTemp      = StringProperty()
  collOutTemp     = StringProperty()
  tankTopTemp     = StringProperty()
  tankBottomTemp  = StringProperty()
  heaterActive    = StringProperty()
  pumpActive      = StringProperty()
  heaterOffTemp   = StringProperty()
  collInTempPlot  = None
  collOutTempPlot  = None
  graph           = Graph()
  zoom            = int
  endDateTime     = datetime.now(tz=pytz.timezone("Europe/London"))
  startDateTime   = None
  
  
  def __init__(self, **kwargs):
    super(SolarControl, self).__init__(**kwargs)
    db.create_connection(self,'OpenSolar.db')
    self.collInTemp = ''
    self.collInTempPlot = MeshLinePlot(color=[1, 0, 0, 1])
    self.collInTempPlot.points  = db.query(self,"select time,value from log where itemId=1 order by time desc") #initalise
    self.collOutTempPlot = MeshLinePlot(color=[1, .6, 0, 1])
    self.collOutTempPlot.points = db.query(self,"select time,value from log where itemId=2 order by time desc") #initalise
    self.graphXSeconds = 60*60
    self.startDateTime = self.endDateTime - timedelta(seconds=self.graphXSeconds)
    Clock.schedule_interval(self.updateScreen, 1)
    
  def updateScreen(self, dt):
    self.collInTemp = str(db.getValue(self,'collInTemp'))
    self.collOutTemp = str(db.getValue(self,'collOutTemp'))
    self.tankTopTemp = str(db.getValue(self,'tankTopTemp'))
    self.tankBottomTemp = str(db.getValue(self,'tankBottomTemp'))
    self.heaterActive = str(db.getValue(self,'heaterActive'))
    self.pumpActive = str(db.getValue(self,'pumpActive'))
    self.heaterOffTemp = str(db.getValue(self,'heaterOffTemp'))
    latestTime = self.collInTempPlot.points[0][0]
    #latestTime = self.collOutTempPlot.points[0][0]
    self.startDateTime = self.endDateTime - timedelta(seconds=self.graphXSeconds)
    
    self.graph.xlabel = "From: " + self.startDateTime.ctime() + "           Until: " + self.endDateTime.ctime()

    self.graph.xmin = (latestTime - self.graphXSeconds)
    self.graph.xmax = latestTime
    
    self.collInTempPlot.points = db.query(self,"select time,value from log where itemId=1 order by time desc")
    self.collOutTempPlot.points = db.query(self,"select time,value from log where itemId=2 order by time desc")
    self.graph.add_plot(self.collInTempPlot)
    self.graph.add_plot(self.collOutTempPlot)

  def tempUp(self):
    self.heaterOffTemp = str(int(self.heaterOffTemp) + 1)
    db.query(self,"UPDATE status SET value = value + 1 WHERE key='heaterOffTemp'")

  def tempDown(self):
    self.heaterOffTemp = str(int(self.heaterOffTemp) - 1)
    db.query(self,"UPDATE status SET value=value - 1 WHERE key='heaterOffTemp'")
    
  def zoomIn(self):
    if self.graphXSeconds != 60*60: #  No lower than 1 hour
      self.graphXSeconds -= 60*60
    
  def zoomOut(self):
    self.graphXSeconds += 60*60

  def history(self):
    latestTime = self.collInTempPlot.points[0][0]
    self.graph = Graph(xlabel="From: " + self.startDateTime.ctime() + "                  Until: " + self.endDateTime.ctime(),
                  ylabel='Temperature (C)',
                  #x_ticks_minor=1,
                  x_ticks_major=self.graphXSeconds,
                  y_ticks_major=10,
                  x_grid_label=True,
                  y_grid_label=True,
                  padding=5,
                  x_grid=True,
                  y_grid=True,
                  xmin=latestTime - self.graphXSeconds,
                  xmax=latestTime,
                  ymin=-10,
                  ymax=120,
                  background_color = (.8,.8,.8,1)
                  )

    self.graph.add_plot(self.collInTempPlot)
    return self.graph

class TopBottom(App,BoxLayout):
  time = StringProperty()
  currentTime = StringProperty(datetime.now(tz=pytz.timezone("Europe/London")).ctime())
  ipAddr = StringProperty()
  solarControl = SolarControl()
  ifName = 'wlp3s0'

  def __init__(self, **kwargs):
    super(TopBottom, self).__init__(**kwargs)
    Clock.schedule_interval(self.updateTime, 1)
    self.ids.history.add_widget(self.solarControl.history(),index=1)  #index=1 add graph before zoom buttons 

  def updateTime(self, dt): 
    self.currentTime = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    try:
      ni.ifaddresses(self.ifName)
      self.ipAddr = ni.ifaddresses(self.ifName)[ni.AF_INET][0]['addr']
    except:
      print("Error: Can't find: "+self.ifName)

  def build(self):
    self.title = 'OpenSolar Controller'
    return self
   
   
if __name__ == '__main__':
    solarControlApp = TopBottom()
    solarControlApp.run()
