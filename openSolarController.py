from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.core.window import Window

from datetime import datetime, timezone, timedelta
import pytz
import time

import netifaces as ni

from kivy.garden.graph import Graph, MeshLinePlot
from kivy.properties import ObjectProperty  
from kivy.app import App  
from kivy.uix.widget import Widget  
from kivy.config import Config

import settings
from openSolarDb import Db

Builder.load_file('./opensolarcontrollerUX.kv')

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
    self.collInTempPlot.points  = self.db.getLog('collInTemp') #initalise
    self.collOutTempPlot = MeshLinePlot(color=[1, .6, 0, 1])
    self.collOutTempPlot.points = self.db.getLog('collOutTemp') #initalise
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
    self.collInTempPlot.points = self.db.getLog('collInTemp')
    self.collOutTempPlot.points = self.db.getLog('collOutTemp')
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

  collInTemp      = StringProperty('0')
  collOutTemp     = StringProperty('0')
  tankTopTemp     = StringProperty('0')
  tankBottomTemp  = StringProperty('0')
  heaterActive    = StringProperty('Off')
  pumpActive      = StringProperty('Off')
  heaterOffTemp   = StringProperty()
  collInTempPlot  = None
  collOutTempPlot = None

  db              = None

  def __init__(self, **kwargs):
    super(Status, self).__init__(**kwargs)
    self.db = Db(settings.dbFile)
    Clock.schedule_interval(self.updateScreen, 1)

  def updateScreen(self, dt):
    self.collInTemp     = self.db.getStatusValueViaName('collInTemp')
    self.collOutTemp    = self.db.getStatusValueViaName('collOutTemp')
    self.tankTopTemp    = self.db.getStatusValueViaName('tankTopTemp')
    self.tankBottomTemp = self.db.getStatusValueViaName('tankBottomTemp')
    self.heaterOffTemp  = self.db.getStatusIntValueViaName('heaterOffTemp')
    self.heaterActive   = "Active" if self.db.getStatusIntValueViaName('heaterActive') == '1' else "Off"
    self.pumpActive     = "Active" if self.db.getStatusIntValueViaName('pumpActive')   == '1' else "Off"

  def tempUp(self):
    self.heaterOffTemp = str(int(self.heaterOffTemp) + 1)
    self.db.statusUPDATE({'heaterOffTemp' : self.heaterOffTemp },'name')

  def tempDown(self):
    self.heaterOffTemp = str(int(self.heaterOffTemp) - 1)
    self.db.statusUPDATE({'heaterOffTemp' : self.heaterOffTemp },'name')


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
      settings.ifName = settings.ifNameFallback  # Fall back to desktop for testing
      print("Error: Can't find: " + settings.ifName)

  def build(self):
    self.title = 'Open Solar Controller'
    #Window.borderless = True
    Window.resizable = False
    Window.size = (800,440)
    Window.top = 0
    Window.left = 0
    Window.position = 'custom'
    return OpenSolarController()

  def close():
    App.get_running_app().stop()

if __name__ == '__main__':
    OpenSolarController().run()
