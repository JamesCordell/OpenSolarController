from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock

from datetime import datetime, timezone, timedelta
import pytz
import time

import netifaces as ni

from kivy.garden.graph import Graph, MeshLinePlot
from kivy.properties import ObjectProperty  
from kivy.app import App  
from kivy.uix.widget import Widget  
from kivy.config import Config
Config.set('graphics','width', '800')
Config.set('graphics','height','480')
#Config.set('graphics','fullscreen','fake')

import settings
from solarDb import Db

Builder.load_file('./opensolarcontrollerUX.kv')
#Builder.load_string("""

#<OpenSolarController>:
  #orientation: 'vertical'
  #Status:
    #size_hint: 1, .9
    #pos_hint: {'center_x': .5, 'center_y': .55}
    #do_default_tab: False
    #TabbedPanelItem:
      #id: status
      #text: 'Status'
      #GridLayout:
        #id: gridLayoutTabbedPanelItem
        #cols: 2
        #Label:
          #text: 'Collector in Temp'
        #Label:
          #text:  root.Status.collInTemp
        #Label:
          #text: 'Collector out Temp'
        #Label:
          #text: root.Status.collOutTemp
        #Label:
          #text: 'Tank Top Temp'
        #Label:
          #text: root.Status.tankTopTemp
        #Label:
          #text: 'Tank Bottom Temp'
        #Label:
          #text: root.Status.tankBottomTemp
        #Label:
          #text: 'Heater Active'
        #Label:
          #text: root.Status.heaterActive
        #Label:
          #text: 'Pump Active'
        #Label:
          #text: root.Status.pumpActive
        #Label:
          #text: 'Heater off temp'
        #GridLayout:
          #cols: 2
          #Label:
            #text: root.Status.heaterOffTemp
          #BoxLayout:
            #orientation: 'vertical'
            #Button:
              #text: 'up'
              #on_release: root.Status.tempUp()
            #Button:
              #text: 'down'
              #on_release: root.Status.tempDown()
    #TabbedPanelItem:
      #text: 'History'
      #BoxLayout:
        #size_hint: 1.9  , 1
        #id: history
        #BoxLayout:
          #orientation: 'vertical'
          #Button:
            #size_hint:  .05, .05 
            #text: '+'
            #on_release: root.History.zoomIn()
          #Button:
            #size_hint:  .05, .05
            #text: '-'
            #on_release: root.History.zoomOut()

    #TabbedPanelItem:
      #id: setup
      #text: 'Setup'
      #RstDocument:
        #text:'\\n'.join(("This is the Open Solar Solar Controller written by James Cordell in python3","You are in the third tab."))
  #GridLayout:
    #id: gridTopBottom
    #cols: 3
    #size_hint: 1, .05
    #font_size: '15sp'
    #Label:
      #text: root.currentTime
    #Label:
      #text: 
    #Label:
      #text: 'IP Address:' + root.ipAddr

#""")

class History(TabbedPanel):

  db              = None
  graph           = Graph()
  zoom            = int
  endDateTime     = datetime.now(tz=pytz.timezone(settings.timeZone))
  startDateTime   = None
  
  def __init__(self, **kwargs):
    super(History, self).__init__(**kwargs)
    self.db = Db(settings.dbFile)
    self.collInTempPlot = MeshLinePlot(color=[1, 0, 0, 1])
    self.collInTempPlot.points  = self.db.query("select time,CAST(value AS INT) from log where itemId=1 order by time desc") #initalise
    self.collOutTempPlot = MeshLinePlot(color=[1, .6, 0, 1])
    self.collOutTempPlot.points = self.db.query("select time,CAST(value AS INT) from log where itemId=2 order by time desc") #initalise
    self.graphXSeconds = 3600  #  Default graph zoom
    self.startDateTime = self.endDateTime - timedelta(seconds=self.graphXSeconds)
    Clock.schedule_interval(self.updateScreen, 1)

  def updateScreen(self, dt):
    latestTime = self.collInTempPlot.points[0][0]
    self.endDateTime = datetime.now(tz=pytz.timezone(settings.timeZone))
    self.startDateTime = self.endDateTime - timedelta(seconds=self.graphXSeconds)
    self.graph.xlabel = "From: " + self.startDateTime.ctime() + "           Until: " + self.endDateTime.ctime()
    self.graph.xmin = (latestTime - self.graphXSeconds)
    self.graph.xmax = latestTime
    self.collInTempPlot.points = self.db.query("select time,CAST(value AS INT) from log where itemId=1 order by time desc")
    self.collOutTempPlot.points = self.db.query("select time,CAST(value AS INT) from log where itemId=2 order by time desc")
    self.graph.add_plot(self.collInTempPlot)
    self.graph.add_plot(self.collOutTempPlot)

  def zoomIn(self):
    if self.graphXSeconds != 3600: #  No lower than 1 hour
      self.graphXSeconds -= 3600

  def zoomOut(self):
    self.graphXSeconds += 3600

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

class Status(TabbedPanel):

  collInTemp      = StringProperty()
  collOutTemp     = StringProperty()
  tankTopTemp     = StringProperty()
  tankBottomTemp  = StringProperty()
  heaterActive    = StringProperty()
  pumpActive      = StringProperty()
  heaterOffTemp   = StringProperty()
  collInTempPlot  = None
  collOutTempPlot = None

  db              = None

  def __init__(self, **kwargs):
    super(Status, self).__init__(**kwargs)
    self.db = Db(settings.dbFile)
    self.collInTemp = ''
    self.heaterOffTemp = self.db.getIntValue('heaterOffTemp')
    Clock.schedule_interval(self.updateScreen, 1)

  def updateScreen(self, dt):
    self.collInTemp     = self.db.getValue('collInTemp')
    self.collOutTemp    = self.db.getValue('collOutTemp')
    self.tankTopTemp    = self.db.getValue('tankTopTemp')
    self.tankBottomTemp = self.db.getValue('tankBottomTemp')
    self.heaterActive   = self.db.getValue('heaterActive')
    self.pumpActive     = self.db.getValue('pumpActive')

  def tempUp(self):
    self.heaterOffTemp = str(int(self.heaterOffTemp) + 1)
    self.db.query("UPDATE `status` SET `value` = `value` + 1 WHERE `key`='heaterOffTemp'")

  def tempDown(self):
    self.heaterOffTemp = str(int(self.heaterOffTemp) - 1)
    self.db.query("UPDATE `status` SET `value` = `value` - 1 WHERE `key`='heaterOffTemp'")


class OpenSolarController(App,BoxLayout):
  currentTime = StringProperty(datetime.now(tz=pytz.timezone(settings.timeZone)).ctime())
  Status = Status()
  History = History()
  ipAddr = StringProperty()

  def __init__(self, **kwargs):
    super(OpenSolarController, self).__init__(**kwargs)
    Clock.schedule_interval(self.updateTime, 1)
    self.ids.history.add_widget(self.History.history(),index=1)  #index=1 add graph before zoom buttons
     
  def updateTime(self, dt): 
    self.currentTime = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    try:
      ni.ifaddresses(settings.ifName)
      self.ipAddr = ni.ifaddresses(settings.ifName)[ni.AF_INET][0]['addr']
    except:
      print("Error: Can't find: " + settings.ifName)

  def build(self):
    self.title = 'Open Solar Controller'
    return OpenSolarController()

if __name__ == '__main__':
    OpenSolarController().run()
