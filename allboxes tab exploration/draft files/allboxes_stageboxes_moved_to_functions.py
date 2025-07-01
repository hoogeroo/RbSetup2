# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""

# PyQt5 classes etc
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Usual Math/Plotting libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# Misc file-handling
import os
import copy
import glob

# Misc utilities
from functools import partial
from scipy.ndimage.filters import gaussian_filter1d

# Timing
import time
from datetime import datetime

# FITS image handling
import astropy.io.fits as fits

# Analogue Digital Conversion
try:
  import adclib
except:
    pass
  
# OUR OWN CONTRIBUTING FILES
import camera_test
from qmsbox import *
import EagleDAC_main as eagle
import multigo_window as mg
import SEC_machinelearning as ML
import Stages as stg
import tek_afg as afg






#import socket
#TCP_IP = '130.216.51.179'
#TCP_PORT = 8833
#BUFFER_SIZE = 50
#datapath='/home/lab/mydata/Data'
MAX_INT=0xfff

#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================

class allboxes(QWidget):
    def __init__(self, tables, datapath=None, parent=None):#ndacs,naoms,ntimes):
      super(allboxes, self).__init__(parent=parent)
      try:
          print(da.GetDevices()) # From qmsbox import: 'import AIOUSB as da';
                                # This is required for all apps using the DAC
      except:
          print("DA not present")
          self.DApresent=False
      if datapath:
          self.datapath=datapath
      else:
          self.datapath='/home/lab/mydata/Data'
      
      # Label data from save-file appropriately so that it can be 
      #         loaded into relevant boxes when the window is populated     
      self.tableinit,self.curvesinit,self.eagledata,\
        self.DIOinit,self.RFinit, self.MGinit,\
          names, self.notes, headers = tables
      
      # Initialising layout
      self.layout = QGridLayout(self)
      self.layout.setSpacing(1)

      # ALL NAMES HERE LOADED IN BY IMPORTING 'daqprops.py'
      # We just store the names in a usable state here
      self.aomlist = [AOM+suffix for AOM in aom_names for suffix in [' Freq',' Ampl']]
      self.DIOnames=dio_names#['RF Ramp Trigger','Unused']
      self.devicenames={'DAC':dac_names, 'DIO':self.DIOnames, 'AOM':self.aomlist,'EagleDAC':EDnames}
      
      self.hlines=1 # Should allow us to add extra stuff to the top of the window without issue
      self.devicelines=np.sum([len(x) for x in self.devicenames.values()])#25 # How many lines to leave between header and group-boxes at bottom of window
      
      # Initialise stage boxes and load data into them from save-file values.
      #         See 'Stages.py' for more detail
      self.Stages=stg.Stages(devdict=self.devicenames, stagenames=names,table=self.tableinit, curves=self.curvesinit, DIOstate=self.DIOinit)
      self.nstages=len(self.Stages.stages)
      if not self.notes:
        self.notes = ["" for i in range(self.nstages)]
        
      self.tablabels = None
      self.dividers = None
      
      # Now we create/place the relevant widgets for everything, and finalise the layout
      self.remakeWindow(initial=True)
      self.setLayout(self.layout)
      
      # We're going to store a set of background pics to use for fringe removal
      self.nBG_max=50
      self.BGimages=None
      # We also store the number of times images have been stored here
      self.nBGstored=0
      
      self.allAOMS=True
      
      self.goaction_complete=True
      self.ML_active=False
      self.MG_active=False
      #try:
      #  s.connect((TCP_IP2, TCP_PORT))
      #  s.close()
      #  self.allAOMS=True
      #except:
      #  print("Check whether 2nd DDS box is available (controls beam for absorption imaging)\n Currently disabled!")
      #  self.allAOMS=False
      
      self.optimiser = None # This will be filled with a ML model - either from scratch, or from file??
                            # Along these lines, the ML model is handled via SEC_machinelearning (referred to as 'ML')
      
      if hasattr(self.parent(), 'bfcam'):
          self.fluo_mode = 'bfcam'#'pdiode'#'bfcam'# Currently only 'bfcam' means anything; using any other string results in using the ADClib card to sample a photodiode.
                              # maybe use 'pdiode' as the other string
          if self.fluo_mode == 'bfcam' and self.parent().bfcam.connected:
              self.parent().bfcam.start_stream()
      else:
          self.fluo_mode = 'pdiode'
      
      try:
          self.adc=adclib.adc()
      except:
          pass
      self.t_initial = 0
              
    #==============================================================================================================
    #==============================================================================================================
    
    def remakeWindow(self,initial=False):
      # This deletes all the old widgets from the layout, letting us start fresh
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      # Relabel relevant stage info for easy referencing
        stge = self.Stages
        self.nstages=len(stge.stages)
        self.stagenames = [stage.name for stage in stge.stages]

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # The thematic sets of buttons/boxes have their own loading functions below
      # We feed in the parameter 'initial' (only =True on start-up, in theory)
      # If initial = True, we create and load in data.
      # If False, we just remake the widgets.
      
      # Design - ALWAYS want DC boxes and device labels on left
        self.makeDCLabels(initial, stge)
      
      # Design - ALWAYS want stage/tab adjustments, Go/MultiGo/ML buttons available (at bottom?)
        self.makeGOLOADbuttons(initial)
        self.makeMGwindow(initial)
        self.makeStageButtons(initial)
        self.makeMLbuttons(initial)
        
      # Design - The stage/EagleDAC/RF boxes will likely be placed in tabs - keep these separate
        self.makeTabs(initial)
        #self.makeStageBoxes(initial, stge)
        #self.makeEDACwindow(initial)
        #self.makeRFwindow(initial)
      # Here endeth the creation of the main set of interactive boxes
        
      # Finally, we refresh the column/stage labels included in the 'Duplicate/Delete Columns'
      #         section of the 'Edit' drop-down menu of the main window
        if not initial:
          self.parent().refreshDupcol()
          self.parent().refreshDelcol()
          
    #==============================================================================================================
    #==============================================================================================================

    def DelCol(self,position='last'):
        if position == 'last':
          position=-1
        self.Stages.delStage(position)
        del self.stagelabels[position]
        self.nstages=len(self.Stages.stages)
        self.remakeWindow()

    def DupCol(self,a=-1,position='last'):
        if position == 'last':
          position=-1
        self.Stages.dupStage(a,position)
        self.nstages=len(self.Stages.stages)
        self.remakeWindow()

    def AddCol(self,time=0,vals=[],DIOstate=[],position='last'):
        if position == 'last':
          position=-1
        self.Stages.addStage(time=time,vals=vals,DIOstate=DIOstate,position=position)
        self.nstages=len(self.Stages.stages)
        self.remakeWindow()
        
    def changeStages(self):
      if self.combostagechange.currentText()=="-" or (self.combostagepos.currentText()=="-" and self.combostagepos.isEnabled()) or (self.combostagetarget.currentText()=="-" and self.combostagepos.isEnabled()):
        print("You must select appropriate stages to proceed!")
      else:
        kind = self.combostagechange.currentText()
        if kind=="Add Stage":
          pos=self.combostagepos.currentIndex()-1
          if pos>self.nstages:
            pos=-1
          self.AddCol(position=pos)
          print(f'Stage added at position {pos} (in front of Stage {self.combostagepos.currentText()})!')
        elif kind=="Delete Stage":
          target=self.combostagetarget.currentIndex()-1
          self.DelCol(position=target)
          print(f'Stage {target} deleted!')
        elif kind=="Duplicate Stage":
          pos=self.combostagepos.currentIndex()-1
          target=self.combostagetarget.currentIndex()-1
          if pos>self.nstages:
            pos=-1
          self.DupCol(a=target,position=pos)
          print(f'Stage {pos} duplicated and placed at position {target} (in front of Stage {self.combostagetarget.currentText()})!')
        elif kind=="Swap Stages":
          pos=self.combostagepos.currentIndex()-1
          target=self.combostagetarget.currentIndex()-1
          if pos>self.nstages:
            pos=-1
          self.Stages.swapStage(target,pos)
          self.remakeWindow()
          print(f'Stages {pos} and {target} swapped!')
        elif kind=="Move Stage":
          pos=self.combostagepos.currentIndex()-1
          target=self.combostagetarget.currentIndex()-1
          if pos>self.nstages:
            pos=-1
          self.Stages.moveStage(target,pos)
          self.remakeWindow()
          print(f'Stage {pos} moved to position {target} (in front of Stage {self.combostagetarget.currentText()})!')
        else:
          print("You must select an appropriate adjustment proceed!")
      
    def setStageChangeBoxes(self, kind):
      self.combostagetarget.clear()
      self.combostagetarget.setEnabled(True)
      
      self.combostagepos.clear()
      self.combostagepos.setEnabled(True)
      if kind=="Add Stage":
        self.combostagetarget.setEnabled(False)
        self.combostagepos.addItem("-")
        self.combostagepos.addItems([stage.name for stage in self.Stages.stages])
        self.combostagepos.addItem("last")
      elif kind=="Delete Stage":
        self.combostagepos.setEnabled(False)
        self.combostagetarget.addItem("-")
        self.combostagetarget.addItems([stage.name for stage in self.Stages.stages])
      elif kind!="[Stage options]":
        self.combostagepos.addItem("-")
        self.combostagepos.addItems([stage.name for stage in self.Stages.stages])
        self.combostagepos.addItem("last")
        self.combostagetarget.addItem("-")
        self.combostagetarget.addItems([stage.name for stage in self.Stages.stages])
      
    #==============================================================================================================
    #==============================================================================================================
    
    def makeTabs(self, initial, tablabels = None, dividers = None):
      stge = self.Stages
      # tablabels should be a list of strings for each tab containing stages
      if tablabels is None and self.tablabels is not None:
        tablabels = self.tablabels
      # dividers should be a list of integers representing the   
      if dividers is None and self.dividers is not None:
         dividers = self.dividers
      else:
        if tablabels is not None:
          print('WARNING: You have labels for tabs but no info on how to divide the stages between them. CHECK CODE')
        else:
          tablabels = ['All Stages']
        dividers = [len(stge.stages)]
      
      # Really want to bookend each set of stages that belong to a particular tab with dividers
      # For 
      # Say we have 10 stages
      if dividers[0] is not 0:
        dividers.insert(0,0)
      if dividers[-1] is not len(stge.Stages):
        dividers.insert(len(stge.Stages),-1)
      
      # The number of dividers is prioritised over the set of tab labels
      # We will add/remove tablabels from the end of the list until the lengths of the two lists make sense
      if len(dividers)-1 != len(tablabels): # dividers are the 'bookend' locations for each tab, remember
        while len(tablabels) > len(dividers) - 1:
          del tablabels[-1]
        while len(tablabels) < len(dividers) - 1:
          tablabels.append(f'Tab {len(tablabels)}')

       tabSet = QTabWidget()    # Tabobject
       self.makeNotes()
       
       tabcontents = []
       for i, label in enumerate(tablabels):
         whichstages = list(dividers[i]:dividers[i+1])
         tabcontents.append(QWidget())
         tablayout = QGridLayout()
         stageset = stge.Stages[whichstages]
         tabcontents[-1].setLayout(makeStageBoxes(initial, stageset, whichstages, layout = tablayout))
         tabSet.addTab(tabcontents[-1], label)
       
       RFEDTab = QWidget()
       RFEDlayout = QGridLayout()
       rfunit = self.makeRFwindow(initial)
       edunit = self.makeEDACwindow(initial)
       RFEDlayout.addWidget(rfunit,0,0,2,5)
       RFEDlayout.addWidget(edunit,2,0,3,5)
       RFEDTab.setLayout(RFEDlayout)
       tabSet.addTab(RFEDTab, 'RF/EagleDAC')
       
       plotTab = QWidget()
       plotlayout = makePlotwindow(initial)
       plotTab.setLayout(plotlayout)
       tabSet.addTab(plotTab, 'Plots')
             
       self.layout.addWidget(TabSet, 0, 2, len(stge.DC)+2, dividers[-1])

    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def makeDCLabels(self,initial, stge, layout = None):
        if layout = None:
          layout = self.layout
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -   
      # Populate DC widgets (boxes in left-hand column)
        self.layout.addWidget(QLabel('DC Values'),1,0)
        for dcID,dc_box in enumerate(stge.DC):
          self.layout.addWidget(dc_box,dcID+2,0)
        if initial:
          self.updateDC()
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      # Populate device labels (labels in second-from-left column)
        devlabels=[QLabel('Time (ms)')]
        for key in self.devicenames.keys():
          if key !='EagleDAC':
            for device in self.devicenames[key]:
              devlabels.append(QLabel(device))
        for labID,label in enumerate(devlabels):
          self.layout.addWidget(label, labID+1,1)
          
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def makeNotes(self):
      if not self.notes:
        self.notes=[""]*self.nstages
      elif len(self.notes)<self.nstages:
        self.notes+=[""]*(self.nstages - len(self.notes))
      for i in range(self.nstages):
        self.stagelabels[i].notes = self.notes[i]
        self.stagelabels[i].clicked.connect(partial(self.labelclicked,i))
        self.stagelabels[i].customContextMenuRequested.connect(partial(self.changetextnotes,i))

    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

    def makeStageBoxes(self, initial, stge, noteIDs, layout = None):
        if layout = None:
          layout = self.layout
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -     
      # We're gonna reconstruct the 'stage label' pushbuttons at the top of the screen
      # Honestly, aside from re-adding the buttons to the layout, I'm not sure whether this is necessary
      
      # First, we make absolutely sure we've removed them all
        if not initial:
          for i in range(len(self.stagelabels)):
            self.stagelabels[-1].deleteLater()
            self.stagelabels[-1].deleteLater()
            del self.stagelabels[-1]

        self.stagelabels=[StageLabel(stage.name) for stage in stge.stages]

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      # Ok, NOW we the stage labels and associated timeboxes to the top of the window
        for stgID,stage in enumerate(stge.stages):
          # Note column placement is 'stage ID + 2';
          #     + 2 -> First two columns are DC values and device labels
          layout.addWidget(self.stagelabels[notIDs[stgID]],0,stgID+2) 
          layout.addWidget(stage.time, 1, stgID+2)
      # and for each stage, we add all associated device boxes
          for boxID,box in enumerate(stage.boxes):
            # Similarly, + 2 -> First two rows are stage labels and associated times
            layout.addWidget(box, boxID+2, stgID+2)
        return layout
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/        
    
    def makeRFwindow(self,initial=False):, layout = None):
      #if layout = None:
      #  layout = self.layout
      if initial:
        self.tek=afg.TekAFG(parent=self)
        self.tek.layout.setContentsMargins(5, 0, 5, 0)
        self.tek.layout.setVerticalSpacing(5)
        if self.RFinit:
          stop_f,start_f,amp,stageind,sweepind = self.RFinit[:5]
        else:
          stop_f,start_f,amp,stageind,sweepind = [1.,4.5,100,0,0]
          
        self.tek.RF_stop_freq.setValue(stop_f)
        self.tek.RF_start_freq.setValue(start_f)
        self.tek.RF_amplitude.setValue(amp)
        self.loadRFStages()
        self.tek.RF_stage_select.currentIndexChanged.connect(self.change_RF_stage)
      else:
        stageind,sweepind=self.tek.RF_stage_select.currentIndex(),self.tek.RF_sweepstyle.currentIndex()
      
      self.loadRFStages()
      self.tek.RF_stage_select.setCurrentIndex(stageind)
      self.tek.RF_sweepstyle.setCurrentIndex(sweepind)
      #layout.addWidget(self.tek,self.hlines+self.devicelines,0,2,5)
      
      #return layout
      return self.tek
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def makeEDACwindow(self,initial=False):#, layout = None):
      #if layout = None:
      #  layout = self.layout
      if initial:
        self.eagledac=eagle.EaglePanel()
        self.eagledac.setFlat(True)
        self.eagledac.layout.setContentsMargins(5, 0, 5, 0)
        self.eagledac.layout.setVerticalSpacing(5)
        for i in range(24):
          self.eagledac.Eagle_boxes[i].setToolTip(EDnames[i])
          try:
            self.eagledac.Eagle_boxes[i].setValue(self.eagledata[i][0])
          except:
            self.eagledac.Eagle_boxes[i].setValue(0)
      #layout.addWidget(self.eagledac,self.hlines+self.devicelines+2,0,3,5)
      return self.eagledac
    
    def makePlotwindow(self, initial=False):
        import matplotlib
        import matplotlib.figure
        from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

        grid = QGridLayout()
        
        self.figure_fluo = matplotlib.figure.Figure()
        self.canvas_fluo = FigureCanvas(self.figure)
        
        self.figure_blackfly = matplotlib.figure.Figure()
        self.canvas_blackfly = FigureCanvas(self.figure)
        
        grid.addWidget(self.canvas_fluo, 2, 0, 15, 15)
        grid.addWidget(self.canvas_blackfly, 2, 15, 15, 15)
        return grid
    
    #==============================================================================================================
    #==============================================================================================================
    
    def makeMGwindow(self,initial=False):
      if initial:
        self.MGPanel=mg.MultiGoPanel()
        self.MGPanel.setFlat(True)
        self.MultiGoButton=QPushButton('MultiGo')
        self.MultiGoButton.setCheckable(True)
        #self.MultiGoButton.setChecked(True)
        self.MultiGoButton.clicked.connect(self.MultiGo_pressed)
        self.MGParamButton=QPushButton('Parameters')
        self.MGParamButton.clicked.connect(self.mgmenu)
        
        self.MGPanel.layout.addWidget(self.MultiGoButton,3,0)
        self.MGPanel.layout.addWidget(self.MGParamButton,3,1)
        self.MGPanel.layout.setContentsMargins(5, 0, 5, 0)
        self.MGPanel.layout.setVerticalSpacing(5)
        
        self.fill_MG_files()
        if self.MGinit:
          self.MGPanel.sbExpFrom.setValue(self.MGinit[0])
          self.MGPanel.sbExpTo.setValue(self.MGinit[1])
          self.MGPanel.cbExpKind.setCurrentIndex(self.MGinit[2])
          self.MGPanel.sbNCycles.setValue(self.MGinit[3])
        else:
          self.MGPanel.sbExpFrom.setValue(0.)
          self.MGPanel.sbExpTo.setValue(1.)
          self.MGPanel.cbExpKind.setCurrentIndex(0)
          self.MGPanel.sbNCycles.setValue(11)
      
      self.layout.addWidget(self.MGPanel,self.hlines+self.devicelines,7,3,2)
      
    def makeStageButtons(self,initial=False):
      if initial:
        self.SCbox = QGroupBox()
        self.SCbox.setFlat(True)
        self.SClayout=QGridLayout()
        #self.SCbox.setTitle('Adjust Stages')
        self.stagechangetypebutton=QPushButton('Enact changes')
        self.stagechangetypebutton.clicked.connect(self.changeStages)
        self.combostagechange = QComboBox()
        self.combostagechange.currentIndexChanged.connect(self.stageboxaction)
        
        self.stagetargetlabel=QLabel("Which Stage?")
        self.combostagetarget=QComboBox()
        self.stageposlabel=QLabel("To where?")
        self.combostagepos=QComboBox()
        
        self.combostagechange.clear()
        self.combostagechange.addItems(["[Stage options]","Add Stage", "Delete Stage", "Duplicate Stage", "Move Stage", "Swap Stages"])   
      
        self.SClayout.addWidget(self.stagechangetypebutton,0,0)
        self.SClayout.addWidget(self.combostagechange,0,1)
        self.SClayout.addWidget(self.stagetargetlabel,1,0)
        self.SClayout.addWidget(self.combostagetarget,1,1)
        self.SClayout.addWidget(self.stageposlabel,2,0)
        self.SClayout.addWidget(self.combostagepos,2,1)
        
        self.SClayout.setContentsMargins(5, 0, 5, 0)
        self.SClayout.setVerticalSpacing(5)
        self.SCbox.setLayout(self.SClayout)
      
      self.layout.addWidget(self.SCbox, self.hlines+self.devicelines, 5, 3,2)
      self.setStageChangeBoxes('')
      
    def stageboxaction(self):
      self.setStageChangeBoxes(self.combostagechange.currentText())
      
    def makeMLbuttons(self,initial=False):
      if initial:
        default_NSteps = 100
        
        self.MLBox = QGroupBox()
        self.MLBox.setFlat(True)
        self.MLLayout = QGridLayout()
        
        self.MLTitle = QLabel('UNFINISHED, DONT USE * ML Optim.')#'Bayesian Optimisation')
        self.MLTrainLabel = QLabel(f'Training in progress: 0/{default_NSteps}')
        self.MLBayesLabel = QLabel('Bayesian iterations: 0; min cost = 0')
        
        self.ParamSetLabel = QLabel('ML Param Set')
        self.cbParamSet=QComboBox()
        self.fill_MG_files(mgo_combobox=self.cbParamSet)
        #self.cbParamSet.currentIndexChanged.connect(self.MLParamSetAction)
        
        self.MLStepsLabel = QLabel('Training Steps')
        self.sbMLNSteps = QSpinBox()
        self.sbMLNSteps.setRange(1, 1000)
        self.sbMLNSteps.setValue(default_NSteps)
        self.sbMLNSteps.setToolTip(f'Range: {self.sbMLNSteps.minimum} -> {self.sbMLNSteps.maximum}')  
        
        self.OptimiseButton=QPushButton('Optimise')
        self.OptimiseButton.setCheckable(True)
        self.OptimiseButton.clicked.connect(self.Optimise_pressed)
        
        self.MLResetButton=QPushButton('Reset Model')
        self.MLResetButton.clicked.connect(self.MLResetAction)
        
        self.MLSaveButton=QPushButton('Save Model')
        self.MLSaveButton.clicked.connect(self.MLSaveAction)
        
        self.MLLoadButton=QPushButton('Load Model')
        self.MLLoadButton.clicked.connect(partial(self.MLLoadAction,load_from_file=True))
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
        self.MLLayout.addWidget(self.MLTitle,0,0,1,2)
        
        self.MLLayout.addWidget(self.ParamSetLabel,1,0)
        self.MLLayout.addWidget(self.cbParamSet,1,1)
        
        self.MLLayout.addWidget(self.MLSaveButton,2,1)
        self.MLLayout.addWidget(self.MLLoadButton,3,1)
        
        self.MLLayout.addWidget(self.OptimiseButton,2,0)
        self.MLLayout.addWidget(self.MLResetButton,3,0)
        
        self.MLLayout.addWidget(self.MLStepsLabel,4,0,1,2)
        self.MLLayout.addWidget(self.sbMLNSteps,4,1,1,2)
        
        self.MLLayout.addWidget(self.MLTrainLabel,5,0,1,2)
        self.MLLayout.addWidget(self.MLBayesLabel,6,0,1,2)
        
        self.MLLayout.setContentsMargins(0, 0, 0, 0)
        self.MLLayout.setVerticalSpacing(0)
        self.MLBox.setLayout(self.MLLayout)
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
      
      self.layout.addWidget(self.MLBox,self.hlines+self.devicelines, 9, 6, 2)
        
    def makeGOLOADbuttons(self,initial=False):
      if initial:
        self.GoBox=QGroupBox()
        self.GoBox.setFlat(True)
        self.GoLayout=QGridLayout()
        
        self.cbMOTLoad=QCheckBox()
        self.cbMOTLoad.stateChanged.connect(self.TimerChange)
        self.MOTLoadLabel=QLabel('Load MOT')
        
        self.cbGOSave=QCheckBox()
        self.GOSaveLabel=QLabel('Save \'MultiGo\' images?')
        self.cbGOSave.setChecked(True)
        
        self.GoButton=QPushButton('Go')
        self.GoButton.clicked.connect(self.GoAction)
        
        self.FluoButton=QPushButton('Fluo. Settings')
        self.FluoButton.clicked.connect(self.FluoAction)
        #self.CycleButton=QPushButton('Cycle')
        #self.CycleButton.clicked.connect(self.CycleAction)
        
        self.fluorescence = 0
        self.fluo_continue = False
        self.fluo_zero = 400 # Use in future to set zero point
        self.fluo_max = 1100
        self.fluo_percentage = 0.8 # Must be number between 0 and 1
        self.fluo_timeout = 60 # units: seconds
        self.fluo_sampletime = 0.1 # units: seconds
        
        self.makeFluoFig()
        self.MOTTimer=QTimer(self)
        self.MOTTimer.timeout.connect(self.MOTTimerAction)
        self.MOTTimer.start(1000*self.fluo_sampletime)
        self.fluo=QLCDNumber()
        
        self.cbPictype=QComboBox()
        for label in ["No picture","One shot","Fluorescence","Shadow image"]: self.cbPictype.addItem(label)
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
        
        self.GoLayout.addWidget(self.MOTLoadLabel,0,0)
        self.GoLayout.addWidget(self.cbMOTLoad,0,1,alignment=Qt.AlignCenter)
        
        self.GoLayout.addWidget(self.GOSaveLabel,1,0)
        self.GoLayout.addWidget(self.cbGOSave,1,1,alignment=Qt.AlignCenter)
        
        self.GoLayout.addWidget(self.GoButton,0,2)
        self.GoLayout.addWidget(self.FluoButton,1,2)
        #self.GoLayout.addWidget(self.CycleButton,1,2)
        
        self.GoLayout.addWidget(self.cbPictype,0,3)
        self.GoLayout.addWidget(self.fluo,1,3)
        
      #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
      
        self.camera=camera_test.camera()
        self.cycling=False
        
      #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        self.GoLayout.setContentsMargins(0, 0, 0, 0)
        self.GoLayout.setVerticalSpacing(0)
        self.GoBox.setLayout(self.GoLayout)
      
      self.layout.addWidget(self.GoBox,self.hlines+self.devicelines+3, 5, 2, 4)
      #self.layout.addWidget(self.cbMOTLoad,self.hlines+self.devicelines+3,6,alignment=Qt.AlignCenter)
      #self.layout.addWidget(self.MOTLoadLabel,self.hlines+self.devicelines+3,5)
      #self.layout.addWidget(self.cbGOSave,self.hlines+self.devicelines+4,6,alignment=Qt.AlignCenter)
      #self.layout.addWidget(self.GOSaveLabel,self.hlines+self.devicelines+4,5)
    
    #==============================================================================================================
    #==============================================================================================================
    
    def datastore(self):
        columns,curves,DIOstate = self.Stages.store()
        RFstate,MGstate = self.RF_MG_store()
        notes = self.stagelabel_store()
        return columns,curves,DIOstate,RFstate,MGstate,notes
          
    def stagelabel_store(self):
      # names are actually stored with the data table columns!
        notes = [label.notes for label in self.stagelabels]
        return notes
      
    def RF_MG_store(self):
        RF_data=[self.tek.RF_stop_freq.value(), self.tek.RF_start_freq.value(), \
          self.tek.RF_amplitude.value(), self.which_RF_stage(), \
            self.tek.RF_sweepstyle.currentIndex()]
          
        MG_data = [self.MGPanel.sbExpFrom.value(),self.MGPanel.sbExpTo.value(),\
          self.MGPanel.cbExpKind.currentIndex(), self.MGPanel.sbNCycles.value()]
        
        return RF_data, MG_data
        
    def RF_MG_load(self,RF_data, MG_data):
      self.tek.RF_stop_freq.setValue(RF_data[0])
      self.tek.RF_start_freq.setValue(RF_data[1])
      self.tek.RF_amplitude.setValue(RF_data[2])
      self.tek.RF_stage_select.setCurrentIndex(RF_data[3])
      self.tek.RF_sweepstyle.setCurrentIndex(RF_data[4])
        
      self.MGPanel.sbExpFrom.setValue(MG_data[0])
      self.MGPanel.sbExpTo.setValue(MG_data[1])
      self.MGPanel.cbExpKind.setCurrentIndex(MG_data[2])
      self.MGPanel.sbNCycles.setValue(MG_data[3])
    
    #==============================================================================================================
    #==============================================================================================================
        
    def loadRFStages(self):
        self.tek.RF_stage_select.clear()
        self.tek.RF_stage_select.addItems(x.name for x in self.Stages.stages)

    def which_RF_stage(self):
        name=self.tek.RF_stage_select.currentText()
        index = [i for i in range(self.nstages) if self.Stages.stages[i].name == name]
        if len(index)==0: return 0
        if len(index)>1: print("TOO MANY CHOICES")
        return index[0]

    def change_RF_stage(self):
        ind = self.which_RF_stage()
        newvalue=self.Stages.stages[ind].time.value()
        if self.tek.RF_sweep_time != newvalue:
          self.tek.RF_sweep_time=newvalue
          self.tek.Change_RF_length()
        self.RF_currentstage = ind
        
    def updateDC(self):
        for DCbox in self.Stages.DC:
            if isinstance(DCbox, DC_DAC_Box):
                DCbox.updateDAC()
                wait(0.1)#time.sleep(0.1)
            elif isinstance(DCbox, DC_AOM_Freq_Box) or isinstance(DCbox, DC_AOM_Ampl_Box):
                DCbox.update()
                wait(0.1)#time.sleep(0.1)

    #==============================================================================================================
    #==============================================================================================================
    # MACHINE LEARNING ACTIONS
    
    def Optimise_pressed(self):
      print(f'Optimise pressed! self.OptimiseButton.isChecked() = {self.OptimiseButton.isChecked()}')
      if self.OptimiseButton.isChecked():
          self.OptimiseButton.setText('Stop')
          self.OptInterrupt=False
          #self.ML_active = True
          self.OptimiseAction()
          self.t_initial = time.time()
      else:
          self.OptInterrupt=True
          self.OptimiseButton.setText('Optimise')
          
    def ML_MOTfull_action(self):
      #print("got here")
      #if not len(self.optimiser.params[0].vals_to_try):
      #  params_to_try = self.suggest_optimal_params(self.optimiser.history['trials'])
      #  #print(f'Trying params: {params_to_try}')
      #  for i, p in enumerate(self.optimiser.params):
      #    p.vals_to_try.append(params_to_try[i])
      params = self.optimiser.params
      #print(params)
      if type(params) is list:
          p = params[0]
      else:
          p = params
      if p.vals_to_try is not None:
        self.loadOptParams(params)     
        self.GoAction()
        self.optimiser.iterate_end()
      else:
        self.optimiser.iterate_stop()
      self.t_initial = time.time()


    def OptimiseAction(self):
        # Plan of attack:
        # - What params are we using? Find these
        # - If no optimiser in existence, make one with param set
        # - Does an optimiser exist? If so, do the parameter sets match? If not, stop and warn user to save,
        #       or ask to overwrite.
        # Once an optimiser is resumed or initialised, start trial runs if model history shorter than X
        # - TELL USER whether progressing with trials, or applying bayesian optimisation on top of this
        # - ALLOW USER TO CANCEL
        # Otherwise iterate repeatedly.
        # - PROVIDE ACCESS TO STATS/BEST PARAMETERS SO FAR (N, OD_max, cost vs param values/trial number)
        # 
        
    # TO DO
      stages=self.Stages.stages
      devind = self.Stages.devIDs
      if self.optimiser is None:
        self.MLParamSetAction()
      else:
        foldA = self.optimiser.model_location.split("/")[-1]; foldB = self.cbParamSet.currentText()
        if not foldA==foldB:
          self.MLParamSetAction()
      
      #eid=self.cbParamSet.currentIndex()
      npts=self.sbMLNSteps.value()
      
      self.checkMLParams(trainingsteps = npts) # This compares the optimiser's current parameter set with the one in the selected .mgo file
      
      self.optimiser.iterate_start()
      #t_i = time.perf_counter()
      
      # Okay, so the above is identical to self.MultiGo currently.
      
      #if self.optimiser.niter < self.optimiser.trainingsteps:
      #  self.optimiser.obtain_training_data()
      #else:
      #  self.optimiser.train_model()
      #  self.optimiser.iterate(N=npts)#1 default, might want to select this? same number as trainingsteps?
      #
      # 
      #QApplication.processEvents()
      #self.updateDC()
      # 
      #return
    
    def saveOptData(self,foldstring, niter):
        filename=f'{foldstring}/Data_{str(niter)}.fit'
        self.parent().mysave(filename, make_jpg = True)
      
    def loadOptParams(self,params):
      stages=self.Stages.stages
      devind = self.Stages.devIDs
      
      for p in params:
            mytype=p.mytype.currentText()
            if p.vals_to_try is None or ((type(p.vals_to_try) is list or type(p.vals_to_try) is np.ndarray) and not len(p.vals_to_try)):
              return
            #try:
            ptype = type(p.vals_to_try)
            #  print(ptype)
            if (ptype is int or ptype is np.float64 or ptype is float):
              myvalue = p.vals_to_try
            else:
              myvalue = p.vals_to_try[0]
            #except:
            #  print(p.vals_to_try)
            #  return
            
            tid=None; cid=None
            if not mytype=='EagleDAC':
                tid=p.time.currentIndex()
            if not mytype=='Time' and not mytype=='RF (amp)':
                cid=p.channel.currentIndex()
                
            #print(f'Time {tid}, Channel {cid}: value={myvalue}')
            if mytype=='Time':
                stages[tid].time.setValue(myvalue)
            elif mytype=='RF (freq)' or mytype=='RF (amp)':
                    #self.tek.Change_RF_length(self.Timeboxes[tid].value()) # Not necessary, I think; should be changed automatically when RF stage select adjusts stage ID.
                rfdisnum=[j for j, x in enumerate(self.Stages.devices['DAC']) if x=='RF disable']
                rfdisableind = devind['DAC'][rfdisnum[0]]
                rfdioind = devind['DIO'][0]
                
                for j in range(len(stages)):
                    stages[j].boxes[rfdioind].setChecked(False)
                    stages[j].boxes[rfdisableind].setValue(5.0)
                    
                stages[tid].boxes[rfdisableind].setValue(0.0)
                stages[tid].boxes[rfdioind].setChecked(True)
                
                self.tek.RF_stage_select.setCurrentIndex(tid)
                if mytype=='RF (freq)':
                    if not cid:
                        self.tek.RF_start_freq.setValue(myvalue)
                        self.tek.Change_RF_startF()
                    else:
                        self.tek.RF_stop_freq.setValue(myvalue)
                        self.tek.Change_RF_stopF()
                else:
                    self.tek.RF_amplitude.setValue(myvalue)
                    self.tek.Change_RF_amplitude()
            elif mytype=='EagleDAC':
                self.eagledac.Eagle_boxes[cid].setValue(myvalue)
            else:
                #print(type(myvalue))
                if type(myvalue) is int or isinstance(myvalue, (np.ndarray, np.generic) ):
                    stages[tid].boxes[devind[mytype][cid]].setValue(myvalue)
                else:
                    box = stages[tid].boxes[devind[mytype][cid]]
                    box.setRange(-30,30)
                    box.setValue(-30)
                    box.setSpecialValueText("Ramp")
                    box.RStart = myvalue[0]; box.REnd = myvalue[1]
    
    def checkMLParams(self, trainingsteps = None):
      if trainingsteps == None:
        trainingsteps = self.sbMLNSteps.value()
      
      mlfullpars = mg.Parameters(self.devicenames,self.stagenames,self.tek)      
      
      name_split = self.cbParamSet.currentText().split('_')
      if len(name_split)==1 or not name_split[0][0:3] == '202':
        if len(name_split)==1:
          fname = self.cbParamSet.currentText()
        else:
          fname = '_'.join(name_split)
        mlfullpars.newread(fname+'.mgo')
        self.MLResetAction()
        self.optimiser.load_params(mlfullpars.params)
        self.optimiser.trainingsteps = trainingsteps
        return
      else: #Basically, if it starts with a time in the year 2023 we assume we've tacked the date onto the start (meaning it's a prior ML run)
        fname = '_'.join(name_split[1:])
        mlfullpars.newread(fname+'.mgo')
      
        # BASIC PRINCIPLE
        # Need to check if we're using a parameter set that is equivalent (device+time-wise) to what the optimiser started with
        # If not, prompt the user to cancel if the optimisation is a mistake
        # Otherwise, reset the optimiser and begin optimisation
        if self.optimiser is None:
          # If we don't have an optimiser, no problem; make it!
            self.optimiser = ML.ExptOptimiser(mlfullpars.params, trainingsteps = trainingsteps, filename = fname, parent=self)
        else:
          if self.optimiser.niter < self.optimiser.trainingsteps:
            self.optimiser.trainingsteps = trainingsteps
          mlpars = mlfullpars.params
          # if we do have an optimiser, lets compare the parameter sets.
          setmatch = True # Assume that they are the same to begin with, for the sake of the while loops.
          if len(mlpars) == len(self.optimiser.params): # If they dont have the same number of parameters, not the same set
            
            newpset = copy.copy(mlpars) # Working with copies so that we can 'pop' each parameter in turn to reduce parameter set size
            oldpset = copy.copy(self.optimiser.params)
            
            while len(newpset)>0 and setmatch: # setmatch starts true, becomes false if no parameter in the optimiser matches a given 
              newp = newpset.pop(0) # extract the first remaining parameter for comparison
              mytype = newp.mytype.currentText()
              
              for old_ix, oldp in enumerate(oldpset):#for oldp in self.optimiser.params:
                if mytype == oldp.mytype.currentText(): # If they arent the same type, dont bother
                  pmatch = True # To take advantage of logical multiplication
                  if not mytype == 'EagleDAC':
                    pmatch *= (newp.time.currentIndex() == oldp.time.currentIndex()) # If the time stages dont match, this will be False
                  if not mytype == 'Time' and not mytype == 'RF (amp)': # Note that the ambiguity here doesnt matter, since we've already checked that the types match by this stage
                    pmatch *= (newp.channel.currentIndex() == oldp.channel.currentIndex()) # If the devices dont match, this will be False
                if pmatch: # pmatch only true if both time and channel match (ie both refer to same box)
                  oldpset.pop(old_ix) # Don't check this member of the old param set again, since we know there was a match
                  break # Only gets us out of the oldp loop, not the newp loop
              setmatch *= pmatch # Important for the while-loop logic; setmatch = False as soon as one of the new parameters doesnt have a partner in the old set, terminating the loop
          else:
            setmatch = False # if the param set lengths dont match, no point checking!
          if not setmatch:
            # The parameter sets dont match! Check whether the user wants to reset the model and begin again or not!
            msg = QMessageBox()
            
            answer = msg.question(self,'',f'The parameters from the .mgo file you\'ve selected ({fname}) don\'t match the current parameter set ({self.optimiser.param_fname}).\n'
                          f'Do you want to continue with the new parameter set? Doing so will reset the optimiser!', msg.Ok | msg.Abort)
            
            if answer == msg.Abort:
              msg.information(self,'','Aborted; Optimiser is untouched.')
            elif answer == msg.Ok:
              self.optimiser.load_params(mlpars)
              self.optimiser.trainingsteps = trainingsteps
              self.MLResetAction()
              msg.information(self,'','The optimiser has been reset with the new parameters')
              
    
    def MLResetAction(self):
        #self.optimiser = None
        #self.checkMLParams()
        if self.optimiser:
          self.optimiser.reset_model()
          self.optimiser.create_folders(filename=self.optimiser.param_fname)
        self.MLTrainLabel = QLabel(f'Training in progress: 0/{self.optimiser.trainingsteps}')
        self.MLBayesLabel = QLabel('Bayesian iterations: 0; min cost = 0')
      
    def MLSaveAction(self):
      # SEE https://scikit-learn.org/stable/model_persistence.html
      # We can save models with pickle
      # save to file named via param set, n trials, date/time?
      # WE NEED TO SAVE THREE THINGS: the model itself; the class attributes; the relevant parameters.
      # Store all three in a special 'models' folder?
    # TO DO
        if self.optimiser:
          self.optimiser.save()
          self.fill_MG_files(mgo_combobox=self.cbParamSet)
        else:
          print('No optimiser has been made yet!')
        
    def MLParamSetAction(self, reload_paramset = True):
      if reload_paramset:
        self.MLLoadAction(load_from_file = False)
      
    def MLLoadAction(self, load_from_file = True):
      # SEE https://scikit-learn.org/stable/model_persistence.html
      # Like saving, we can load models with pickle
      # load from file named via param set, n trials, date/time?
      # WE NEED TO LOAD THREE THINGS: the model itself; the class attributes; the relevant parameters.
      # Retrieve all three from a special 'models' folder?
    # TO DO
        if load_from_file:
          print(f'Loading from file - check that dialog opens!')
          fullname,str_ignore = QFileDialog.getOpenFileName(self, 'Open file',f'{os.getcwd()}/models/',"Optimiser (*.mgo)")
          fname = fullname.split('/')[-1][:-4]
          path = '/'.join(fullname.split('/')[:-1])
          print(f'fullname = {fullname}; fname = {fname}; path = {path}')
        else:
          fname=self.cbParamSet.currentText()
          fullname=f'{os.getcwd()}/{fname}.mgo'
          path=None
        
        print(f'Using file: {fullname}')
        
        mlpars = mg.Parameters(self.devicenames,self.stagenames,self.tek)
        mlpars.newread(fullname)
        
        
        
        if not self.optimiser:
          trainingsteps = self.sbMLNSteps.value() 
          self.optimiser = ML.ExptOptimiser(mlpars.params, trainingsteps = trainingsteps, filename = fname, folder=path, parent=self)
        
        if os.path.isfile(f'{fullname[:-4]}.pkl'):
          self.optimiser.load(mlpars.params, name=f'{fullname[:-4]}.pkl')
        else:
          print(f'No prior model for {fname}.mgo found. Starting fresh!')
          self.optimiser.load(mlpars.params)
          self.optimiser.param_fname = fname

        if load_from_file:
          self.fill_MG_files(mgo_combobox=self.cbParamSet)
          mgo_index = self.cbParamSet.findText(self.optimiser.mydate)
          self.cbParamSet.setCurrentIndex(mgo_index)
        
    #==============================================================================================================
    #==============================================================================================================
    def labelclicked(self,i):
        #print("Hello",i)
        if self.Stages.stages[i].enabled:
            for box in self.Stages.stages[i].boxes:
              box.setEnabled(False)
            self.Stages.stages[i].enabled=False
            self.Stages.stages[i].time.setEnabled(False)
        else:
            for box in self.Stages.stages[i].boxes:
              box.setEnabled(True)
            self.Stages.stages[i].enabled=True
            self.Stages.stages[i].time.setEnabled(True)
        
    def changetextnotes(self,i):
        #print("Hello 2 ",i)
        label=self.stagelabels[i]
        dialog = LabelDialog(label.text(),label.notes)
        if dialog.exec_():
          newname=dialog.namebox.text()
          self.Stages.stages[i].name=newname
          label.setText(newname)
          label.notes=dialog.notesbox.toPlainText()
          self.notes[i]=label.notes
          self.remakeWindow()

    #==============================================================================================================
    #==============================================================================================================

    def loadData(self):
        tempstages = self.Stages.stages
        stages=[]
        for i in range(len(tempstages)):
          if tempstages[i].enabled:
            stages.append(tempstages[i])
        
        oldstages=[tempstages[i] for i in range(len(tempstages)) if tempstages[i].enabled] # Ideally this should only return the set of stages that are enabled - hopefully in order!
                                                                        # This way, you can enable/disable stages at will without affecting how data is loaded/used
        #print([stage.name for stage in stages])
        #print(oldstages)
        devIDs = self.Stages.devIDs
        self.totaltime=0.0
        self.timestep=0.05/(1.0+0.0625e-3)
        #self.totaltime=sum([stage.time.value() for stage in stages])
        #for stage in stages:
          #if stage.enabled:
        self.totaltime=np.sum([stage.time.value() for stage in stages])
        nsteps=int(self.totaltime/self.timestep + 1) # assuming timesteps of 0.1 ms
        prefire_timesteps = [int(round(dac_prefire[row]/self.timestep)) for row in range(len(self.devicenames['DAC']))]

        data=np.zeros([nsteps,len(self.devicenames['DAC'])]).astype(int)
        timestepstilnow=0
        thetime=0.0
        msg='LOAD,'
        msg2='LOAD,'
        for tid in range(len(stages)):
          #if stages[tid].enabled:
            stagetime = stages[tid].time.value()
            timesteps=int(stagetime/self.timestep)
            t_range = np.arange(timesteps)
            for row in range(len(self.devicenames['DAC'])):
                box_val = stages[tid].boxes[row].value()
                if box_val > 0: 
                    box_val = dac_conversions[row].getval(box_val)
                    
                step_initial = timestepstilnow - prefire_timesteps[row]
                step_final = step_initial + timesteps
                #if row == 2:
                    #print(f'Device = {self.devicenames["DAC"][row]}: val = {box_val}')
                
                if (box_val < -25):
                    rstart = dac_conversions[row].getval(stages[tid].boxes[row].RStart)
                    rend = dac_conversions[row].getval(stages[tid].boxes[row].REnd)
                    #print(f'Device = {self.devicenames["DAC"][row]}: rstart={rstart}; rend={rend}')
                    
                    temp = rstart + ((rend-rstart)/timesteps) * t_range
                    
                #elif (box_val < -15):
                #    offset = dac_conversions[row].getval(stages[tid].boxes[row].LOffset)
                #    lAmp = dac_conversions[row].getval(stages[tid].boxes[row].LAmp)
                #    lTc = dac_conversions[row].getval(stages[tid].boxes[row].LTc)
                #    
                #    temp = offset + lAmp/(1.0+(t_range * self.timestep/lTc)**2)
                    
                elif ((box_val>=0.0) and (box_val<=5.0)):
                    temp = box_val * np.ones(timesteps)
                
                #temp[:,np.newaxis] is a big muckaround to force the result to be a column vector, as per documentation on 'numpy.tranpose'
                #data[step_initial : step_final, row] = np.round(temp[:,np.newaxis] * MAX_INT/5.0).astype(int)#[:]
                #print(f'tid = {tid}; row = {row}; final = {step_final};  initial = {step_initial}; timesteps = {timesteps}; len(temp) = {len(temp)}')
                      ##f'data = {data[step_initial : step_final, row]}')
                #print(data.shape)
                #print(data[step_initial : step_final, row])
                #print(data[step_initial : step_final, row].shape)
                #print(np.round(temp * MAX_INT/5.0).astype(int).shape)
                data[step_initial : step_final, row] = np.round(temp * MAX_INT/5.0).astype(int)#[:]
                
                
                #for t in range(timesteps):
                    #i = t + timestepstilnow
                    #i2 = i - prefire_timesteps[row]
                    #temp = dac_conversions[row].getval(stages[tid].boxes[row].value())
                    #if ((temp>=0.0) and (temp<=5.0)):
                        #data[i2,row]=int(temp*MAX_INT/5.0)
                    #elif (temp==-20.0):

                    #elif (temp==-30.0):
                        #rstart = dac_conversions[row].getval(stages[tid].boxes[row].RStart)
                        #rend = dac_conversions[row].getval(stages[tid].boxes[row].REnd)
                        
                        #tmp2=rstart + t*(rend-rstart)/timesteps
                        #data[i2,row]=int(tmp2*MAX_INT/5.0)
            timestepstilnow+=timesteps
            self.data=data
            
            time_aom = round(thetime*10)*100
            if len(self.devicenames['AOM'])>0:
              for AOM in range(4):#ONLY doing the first 4 AOMs #range(int(len(self.devicenames['AOM'])/2)): # Prepare message for 1st AOM
                t1=devIDs['AOM'][2*AOM]
                if tid==0: # We need a special case for the first column, we need to compare to DC value rather than previous column
                    t2=AOM+10
                    temp=stages[tid].boxes[t1].value()
                    if round(temp-self.Stages.DC[t1].value())!=0:
                        msg=msg+str(t2)+','+'FREQ,'+str(AOM)+','+str(temp)+','
                    
                    ampval=stages[tid].boxes[t1+1].value()
                    temp=aom_amp_conversions[AOM].getval(ampval)
                    if round(100*(ampval-self.Stages.DC[t1+1].value()))!=0: # Be aware - fstring formatting is to force 2dp rounding so that DDS doesnt get upset
                        msg=msg+str(t2)+','+'AMPL,'+str(AOM)+','+f'{temp:.2f}'+','#str(temp)+','
                else:
                    temp=stages[tid].boxes[t1].value()
                    if round(temp-stages[tid-1].boxes[t1].value())!=0:
                        msg=msg+str(time_aom+AOM)+','+'FREQ,'+str(AOM)+','+str(temp)+','
                        
                    ampval=stages[tid].boxes[t1+1].value()
                    temp=aom_amp_conversions[AOM].getval(ampval)
                    if round(100*(ampval-stages[tid-1].boxes[t1+1].value()))!=0: # Be aware - fstring formatting is to force 2dp rounding so that DDS doesnt get upset
                        msg=msg+str(time_aom+AOM)+','+'AMPL,'+str(AOM)+','+f'{temp:.2f}'+','#str(temp)+','
              
              for num,DIOid in enumerate(devIDs['DIO']):
                if tid==0:
                    t1=self.Stages.DC[DIOid].isChecked()
                else:
                    t1=stages[tid-1].boxes[DIOid].isChecked()
                t2=stages[tid].boxes[DIOid].isChecked()
                if (t1 != t2):
                    msg=msg+str(time_aom+14+num)+",TRIG,"+str(num)+','+str(int(t2))+','
                    
            if (len(self.devicenames['AOM'])>8) and self.allAOMS:
              n2=int(len(self.devicenames['AOM'])/2) - 4
              for AOM in range(n2): # Same for second AOM
                #t1=2*AOM+self.nDACs+8
                t1=devIDs['AOM'][2*AOM+8]
                if tid==0:
                    temp=stages[tid].boxes[t1].value()
                    #print(temp,t1,stages[tid].boxes[t1].value())
                    if round(temp-self.Stages.DC[t1].value())!=0:
                        msg2=msg2+'10,FREQ,'+str(AOM)+','+f'{temp:.0f}'+','
                        
                    ampval=stages[tid].boxes[t1+1].value()
                    temp=aom_amp_conversions[AOM+4].getval(ampval)
                    if temp < -20:
                        rbox = stages[tid].boxes[t1+1]
                        #print(f'ramp start: {rbox.Rstart}; ramp end: {rbox.REnd}; stage time: {stagetime}')
                        msg2 += f'10,RAMP,{str(AOM)},{rbox.RStart},{rbox.REnd},{stagetime},'
                    elif round(100*(ampval - self.Stages.DC[t1+1].value()))!=0:
                        print(f'tid:{tid}, AOM = {AOM}: value = {ampval}, adjusted = {temp:.3f}')
                        msg2=msg2+'10,AMPL,'+str(AOM)+','+f'{temp:.3f}'+','
                else:
                    temp=stages[tid].boxes[t1].value()
                    if round(temp-stages[tid-1].boxes[t1].value())!=0:
                        msg2=msg2+str(time_aom)+',FREQ,'+str(AOM)+','+f'{temp:.0f}'+','
                        
                    ampval=stages[tid].boxes[t1+1].value()
                    temp=aom_amp_conversions[AOM+4].getval(ampval)
                    if temp < -20:
                        rbox = stages[tid].boxes[t1+1]
                        msg2 += f'{str(time_aom)},RAMP,{str(AOM)},{rbox.RStart},{rbox.REnd},{stagetime},'
                    elif round(100*(ampval - stages[tid-1].boxes[t1+1].value()))!=0:
                        print(f'tid:{tid}, AOM = {AOM}: value = {ampval}, adjusted = {temp:.3f}')
                        msg2=msg2+str(time_aom)+',AMPL,'+str(AOM)+','+f'{temp:.3f}'+','        
            thetime=thetime+stagetime
        msg=msg+"F"
        msg2=msg2+"F"
        if (len(msg)>6):
            #print(msg)
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send(msg.encode())
            #print(s.recv(5))
            s.close()
        if (len(msg2)>6) and self.allAOMS:
            print(msg2)
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP2, TCP_PORT))
            s.send(msg2.encode())
            s.recv(5)
            s.close()
        self.nsamples=timestepstilnow

    #==============================================================================================================
    #==============================================================================================================

    def GoAction(self, check_trap = False):
        self.goaction_complete = False
        self.allAOMS=True
        
        self.MOTTimer.stop()
        bfcam = self.parent().bfcam
        # Making sure our server connection is sorted
        if self.fluo_mode == 'bfcam' and bfcam.connected:
          bfcam.end_stream()
          print('Ended stream...')
        elif not bfcam.connected:
          bfcam.conn()
        
        wait(0.15)
        bfcam.take_pics() # NOTE: Blackfly cam needs ~1sec after turning on trigger mode (which is a part of camera set-up on server when take_pics() is used) before it is ready
        wait(1) # Need at least 1sec before blackfly ready for pictures; I'm trying to keep this as short as possible while still working
        self.pulse_off()        
        wait(0.15)
        #try:
        #    s.connect((TCP_IP2, TCP_PORT))
        #    s.close()
        #    self.allAOMS=True
        #except:
        #    print("Check whether 2nd DDS box is available (controls beam for absorption imaging)\n Currently disabled!")
        #    self.allAOMS=False
        
        #start_time=time.time()
        self.loadData()
        #end_time=time.time()
        #elapsed=end_time-start_time
        #print("Elapsed for Loaddata ", elapsed)
        #wait(0.1)
        
        
        
        #self.pulse_off()
        plt.close('all')
        
        self.doGo(check_trap = check_trap)
        
        if self.cbGOSave.checkState() and self.MOTfull_flag and not (self.MG_active or self.ML_active):
          mydate=datetime.now().strftime('%Y%m%d%H%M')
          nfolds=len([f for f in os.listdir(self.datapath) if f.startswith(mydate) and f.endswith('.fit')])
          if not nfolds:
            filename=f'{self.datapath}/0 Individual Images/Go_{mydate}.fit'
          else:
            filename=f'{self.datapath}/0 Individual Images/Go_{mydate}_{nfolds}.fit'
          self.parent().mysave(filename)
          
        self.updateDC()
        wait(0.1)#time.sleep(0.1)
        self.makeFluoFig()
        self.MOTTimer.start(round(self.fluo_sampletime*1000))
        if self.fluo_mode == 'bfcam' and bfcam.connected:
          print('Restarting stream')
          bfcam.start_stream()
        
        if self.cbMOTLoad.isChecked() or self.MG_active or self.ML_active:
          self.pulse_on()
        self.goaction_complete = True
    
    def FluoAction(self):
        #print(self.fluo_zero, self.fluo_max, self.fluo_percentage, self.fluo_timeout, self.fluo_sampletime)
        dialog = FluoDialog(self.fluo_zero, self.fluo_max, self.fluo_percentage, self.fluo_timeout, self.fluo_sampletime, self.adc)
        if dialog.exec_():
          #print('[self.fluo_zero, self.fluo_max, self.fluo_percentage,self.fluo_timeout, self.fluo_sampletime] = {dialog.values}')
          [self.fluo_zero, self.fluo_max, self.fluo_percentage,self.fluo_timeout, self.fluo_sampletime] = dialog.values
        #print(self.fluo_zero, self.fluo_max, self.fluo_percentage, self.fluo_timeout, self.fluo_sampletime)
    
    def CycleAction(self):
        print('CycleAction')
        if self.cycling:
            self.cycling=False
            self.CycleButton.setText('No Cycle')
            #self.EDRE.stop()
        else:
            self.loadData()
            self.CycleButton.setText('Cycling')
            self.cycling=TrueTimebox
            if self.sbNCycles.value()==0:
                while self.cycling:
                    self.doGo()
                    print(self.totaltime)
                    time.sleep(0.001*self.totaltime+2)
            else:
                for i in range(self.sbNCycles.value()):
                    self.doGo()
                    time.sleep(0.001*self.totaltime+2)
                    
    def checkMOTFull(self):
        self.t_init = time.time()
        self.t_final = time.time()
        
        self.makeFluoFig()
        self.MOTTimer.start(round(self.fluo_sampletime*1000))

        while (not self.MOTfull_flag) and (self.t_final - self.t_init < self.fluo_timeout):#(self.t_final - self.t_init < self.fluo_timeout):
          QApplication.processEvents()
        self.MOTTimer.stop()
        
        fluo_threshold = (self.fluo_max - self.fluo_zero) * self.fluo_percentage + self.fluo_zero
        if not self.MOTfull_flag:
          print(f'{self.fluo_timeout} seconds has elapsed without seeing enough fluorescence!\n'
                f' Last fluorescence observed: {self.fluorescence} a.u.; Needed {fluo_threshold} a.u.\n'
                f'allboxes.doGo aborted.')
          return self.fluo_continue # Allows external setting where multigo/machine learning continue despite uneven fluorescence
        else:
          print(f'Threshold fluorescence surpassed! (Observed: {self.fluorescence} a.u.; Needed {fluo_threshold} a.u.)')
          return True
                    
    def doGo(self, check_trap = False):
        #self.pulse_off()
        self.MOTfull_flag = True #If we skip checking the trap, this makes sure that everything remains happy.
        self.change_RF_stage()
        
        # Checking whether MOT is sufficiently populated
        # If not enough fluorescence by time-out, we forget about attempting this.
        if False:#check_trap:
            self.MOTfull_flag = False# Note that this starts off set to False at the beginning of each expt attempt.
             # We can subsequently check elsewhere whether the last attempt failed due to low population using 'if not self.MOTfull_flag:'
            fullflag = self.checkMOTFull()
            if not fullflag:
                return
        #self.pulse_off() # Only stop loading once we know we have enough particles!
        #wait(0.5)#time.sleep(1)
        
        # - - - - -
        nshots=self.cbPictype.currentIndex()
        plt.close()
        if (nshots>0):
            if self.parent().blackfly_action.isChecked():
              self.parent().bfcam.remove_old_photos()#shoot(nshots)
              #a=1
            if self.parent().princeton_action.isChecked():
              self.camera.shoot(nshots)
              
        msg='EXPT'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((TCP_IP, TCP_PORT))
            #s.setblocking(0)
            s.send(msg.encode())
            #print(s.recv(5))
        wait(0.1)#time.sleep(0.1)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if len(self.devicenames['AOM'])>8  and self.allAOMS:
                s.connect((TCP_IP2, TCP_PORT))
                s.send(msg.encode())
                #s.setblocking(0)
                #print(s.recv(5))
        wait(0.1)#time.sleep(0.1)
        
        nsamples=self.data.shape[0]
        data = self.data.flatten('C').astype(np.ushort)
        #print(data)
        datalen=data.shape[0]
        if (datalen<=0x10001) :
            firstval=data[0]+0x1000
            data2=np.ones(0x10001,dtype=np.ushort)*firstval
            data2[0:datalen]=data[:]
            data=data2
        data[datalen-1]+=0x8000
        datalen=data.shape[0]
        freq=20000

        result=da.DACOutputProcess(0,freq,datalen,data) # SEE AIOUSB.py
        #wait(1)#time.sleep(1) # give time for the photos to arrive

        if (nshots>0):
            if self.parent().blackfly_action.isChecked():
              #self.parent().bfcam.shoot(nshots)
              #print(self.BGimages)
              if self.BGimages is None:
                self.BGimages=np.zeros([\
                  self.parent().bfcam.dims[0]-2*self.parent().bfcam.lowpassflag,\
                  self.parent().bfcam.dims[1]-2*self.parent().bfcam.lowpassflag,\
                  self.nBG_max])
                self.nBGstored = 0
              
              self.BGimages, bg_resetflag = self.parent().bfcam.show(nshots,self.BGimages,self.nBGstored)
              self.plotBlackfly()
              if bg_resetflag:
                self.nBGstored = 1
              else:
                self.nBGstored+=1
            if self.parent().princeton_action.isChecked():
              self.camera.shoot(nshots)
              self.mydata=self.camera.read()
              plt.imshow(self.mydata)
              plt.draw() # Apparently this is preferred over show() for gui applications
              #plt.show()
        f=open('test.txt','w')
        for i in range(self.data.shape[0]):
          for j in range(self.data.shape[1]):
            f.write("%d \n" % self.data[i,j])
        f.close()
        
    #==============================================================================================================
    #==============================================================================================================
          
    def mgmenu(self):
        currentindex=self.MGPanel.cbExpKind.currentIndex()
        mg.multigomenu(self.MGPanel,self.devicenames,[self.Stages.stages[i].name for i in range(self.nstages)],self.tek)
        self.fill_MG_files()
        try:
          self.fill_MG_files(mgo_combobox = self.cbParamSet)
        except:
          print('ML parameter combo box doesn\'t exist? Check')
        self.MGPanel.cbExpKind.setCurrentIndex(currentindex) # returns to previous parameter set, rather than new one!

    def fill_MG_files(self, mgo_combobox=None):
        if mgo_combobox is None:
          mgo_combobox = self.MGPanel.cbExpKind
        
        flist = []
        # Adjusted so that we can also give this the machine-learning combobox
        mgo_combobox.clear()#self.MGPanel.cbExpKind.clear()
        if not mgo_combobox:
          flist=sorted(glob.glob("*.mgo"))
        
        if hasattr(self,'cbParamSet') and mgo_combobox == self.cbParamSet:
          for f in sorted(glob.glob('./models/*/*.mgo')):
            #print(f)
            flist.append(f.split('/')[2]+'.mgo')
          
        for item in flist:
          sitem=item[:-4]
          mgo_combobox.addItem(sitem)
          
    def MultiGo_pressed(self):
      if self.MultiGoButton.isChecked():
          
          self.MultiGoButton.setText('Stop')
          self.MGinterrupt=False
          self.MG_active=True
          self.t_initial = time.time()
          self.MultiGo()
      else:
          self.MGinterrupt=True
          self.MultiGoButton.setText('MultiGo')
          self.MG_active=False
          
    def MG_set_param_data(self):
      for p in self.mg_params:
        p.vals_to_try = []
        
        start = float(p.Startbox.value())
        stop = float(p.Stopbox.value())
        if self.mg_npts > 1:
          vals = np.linspace(start, stop, self.mg_npts)
        else:
          vals = [start]
          
        p.vals_to_try = list(vals)
        # - - - - - -
        if not p.mytype=='EagleDAC':
          p.tid = p.time.currentIndex()
        if not p.mytype=='Time' and not p.mytype=='RF (amp)':
          p.cid = p.channel.currentIndex()
          
    def MultiGo(self):
      # New version with event driving
      self.MG_active=True
      self.stages=self.Stages.stages
      self.devind = self.Stages.devIDs
      
      self.MG_index=0
      self.mg_eid=self.MGPanel.cbExpKind.currentIndex()
      self.mg_npts=self.MGPanel.sbNCycles.value()
      #if eid<3:
      #  b_val=self.MGPanel.sbExpFrom.value()
      #  e_val=self.MGPanel.sbExpTo.value()
      #  dacid=self.MGPanel.cbExpKind.currentIndex()+3
      #else:
      
      fname=self.MGPanel.cbExpKind.currentText()+'.mgo'
      mgpars = mg.Parameters(self.devicenames,self.stagenames,self.tek)
      mgpars.newread(fname)
      self.mg_params=mgpars.params
      
      #self.eagledac.Eagle_boxes[dacid].setPalette(QPalette)
      self.mydate=datetime.now().strftime('%Y%m%d%H%M')
      nfolds=len([f for f in os.listdir(self.datapath) if f.startswith(self.mydate)])
      if not nfolds:
        os.mkdir(f'{self.datapath}/{self.mydate}')
      else:
        os.mkdir(f'{self.datapath}/{self.mydate}_{nfolds}')
      self. MG_t_init = time.perf_counter()  
      
      for p in self.mg_params:
            p.mytype=p.mytype.currentText()
            b_val=float(p.Startbox.value())
            e_val=float(p.Stopbox.value())
            p.myvalue=np.zeros(self.mg_npts)
            if self.mg_npts>1:
              for i in range(self.mg_npts):
                #if not mytype=='RF (freq)':
                p.myvalue[i]=b_val+i*(e_val-b_val)/(self.mg_npts-1)
                #else:
                #    myvalue=b_val+i*(e_val-b_val)/(npts)
                #    nextval=b_val+(i+1)*(e_val-b_val)/(npts)
            else:
                p.myvalue[0]=b_val
            if not p.mytype=='EagleDAC':
                p.tid = p.time.currentIndex()
            if not p.mytype=='Time' and not p.mytype=='RF (amp)':
                p.cid = p.channel.currentIndex()
            #this stuff below to be updated
            #elif mytype=='RF (freq)' or mytype=='RF (amp)':
                    ##self.tek.Change_RF_length(self.Timeboxes[tid].value()) # Not necessary, I think; should be changed automatically when RF stage select adjusts stage ID.
                #rfdisnum=[j for j, x in enumerate(self.Stages.devices['DAC']) if x=='RF disable']
                #rfdisableind = devind['DAC'][rfdisnum[0]]
                #rfdioind = devind['DIO'][0]
                
                #for j in range(len(stages)):
                    #stages[j].boxes[rfdioind].setChecked(False)
                    #stages[j].boxes[rfdisableind].setValue(5.0)
                    
                #stages[tid].boxes[rfdisableind].setValue(0.0)
                #stages[tid].boxes[rfdioind].setChecked(True)
                
                #self.tek.RF_stage_select.setCurrentIndex(tid)
                #if mytype=='RF (freq)':
                    #if not cid:
                        #self.tek.RF_start_freq.setValue(myvalue)
                        #self.tek.Change_RF_startF()
                    #else:
                        #self.tek.RF_stop_freq.setValue(myvalue)
                        #self.tek.Change_RF_stopF()
                #else:
                    #self.tek.RF_amplitude.setValue(myvalue)
                    #self.tek.Change_RF_amplitude()
            
    def MG_update_params(self): # can just use self.loadOptParams(self.mg_params) 
                                # if we have another function that pushes linspaces into each set of params (via p.values_to_try)
                                # and deletes them afterwards
      for p in self.mg_params:
        if p.mytype=='Time':
           self.stages[p.tid].time.setValue(p.myvalue[self.MG_index])
        elif p.mytype=='EagleDAC':
                self.eagledac.Eagle_boxes[p.cid].setValue(p.myvalue[self.MG_index])
        elif p.mytype=='RF (freq)':
             if p.cid==0:
                self.tek.RF_start_freq.setValue(p.myvalue[self.MG_index])
             else:
                self.tek.RF_stop_freq.setValue(p.myvalue[self.MG_index])
        elif p.mytype == 'RF (amp)':
            self.tek.RF_amplitude.setValue(p.myvalue[self.MG_index])
        else:
                self.stages[p.tid].boxes[self.devind[p.mytype][p.cid]].setValue(p.myvalue[self.MG_index])
      (self.MG_index)+=1
      
    def MG_MOTfull_action(self):
      #print("got here")
      self.MGPanel.mgCount.setText(str(self.MG_index+1)+' of '+str(self.mg_npts))
      self.MG_update_params()
      
      self.GoAction()
      #self.loadData()
      #self.doGo()
      #self.updateDC()
      #self.pulse_on()
      self.t_initial = time.time()
      #print(self.MG_index,self.mg_npts)
      if self.cbGOSave.checkState() and self.MOTfull_flag:
            filename=f'{self.datapath}/{self.mydate}/Data_{str(self.MG_index)}.fit'
            self.parent().mysave(filename)
      else:
            t_f = time.perf_counter()  
            print(f'MultiGo failed due to lack of atoms during experiment {i+1}, having reached the end of the {self.fluo_timeout}s time-out. It had been running for {t_f - self.MG_t_init:.3f} seconds.')
            self.MultiGoButton.setText('MultiGo')
            self.MultiGoButton.setChecked(False)
            return
      if self.MG_index>=(self.mg_npts):
        self.MG_active=False
        self.MultiGoButton.setText('MultiGo')
        self.MultiGoButton.setChecked(False)
      
      
    def MultiGo2(self):
      stages=self.Stages.stages
      devind = self.Stages.devIDs
      
      eid=self.MGPanel.cbExpKind.currentIndex()
      npts=self.MGPanel.sbNCycles.value()
      #if eid<3:
      #  b_val=self.MGPanel.sbExpFrom.value()
      #  e_val=self.MGPanel.sbExpTo.value()
      #  dacid=self.MGPanel.cbExpKind.currentIndex()+3
      #else:
      fname=self.MGPanel.cbExpKind.currentText()+'.mgo'
      mgpars = mg.Parameters(self.devicenames,self.stagenames,self.tek)
      mgpars.newread(fname)
      #self.eagledac.Eagle_boxes[dacid].setPalette(QPalette)
      mydate=datetime.now().strftime('%Y%m%d%H%M')
      nfolds=len([f for f in os.listdir(self.datapath) if f.startswith(mydate)])
      if not nfolds:
        os.mkdir(f'{self.datapath}/{mydate}')
      else:
        os.mkdir(f'{self.datapath}/{mydate}_{nfolds}')
        
      t_i = time.perf_counter()  
      for i in range(npts):
        self.MGPanel.mgCount.setText(str(i+1)+' of '+str(npts))
        #if (eid<3):
        #    myvalue=b_val+i*(e_val-b_val)/(npts-1)
        #    #print(myvalue)
        #    self.eagledac.Eagle_boxes[dacid].setValue(myvalue)
        #else:
        for p in mgpars.params:
            mytype=p.mytype.currentText()
            b_val=float(p.Startbox.value())
            e_val=float(p.Stopbox.value())
            if npts>1:
                #if not mytype=='RF (freq)':
                myvalue=b_val+i*(e_val-b_val)/(npts-1)
                #else:
                #    myvalue=b_val+i*(e_val-b_val)/(npts)
                #    nextval=b_val+(i+1)*(e_val-b_val)/(npts)
            else:
                myvalue=b_val
            if not mytype=='EagleDAC':
                tid=p.time.currentIndex()
            if not mytype=='Time' and not mytype=='RF (amp)':
                cid=p.channel.currentIndex()
            if mytype=='Time':
                stages[tid].time.setValue(myvalue)
            elif mytype=='RF (freq)' or mytype=='RF (amp)':
                    #self.tek.Change_RF_length(self.Timeboxes[tid].value()) # Not necessary, I think; should be changed automatically when RF stage select adjusts stage ID.
                rfdisnum=[j for j, x in enumerate(self.Stages.devices['DAC']) if x=='RF disable']
                rfdisableind = devind['DAC'][rfdisnum[0]]
                rfdioind = devind['DIO'][0]
                
                for j in range(len(stages)):
                    stages[j].boxes[rfdioind].setChecked(False)
                    stages[j].boxes[rfdisableind].setValue(5.0)
                    
                stages[tid].boxes[rfdisableind].setValue(0.0)
                stages[tid].boxes[rfdioind].setChecked(True)
                
                self.tek.RF_stage_select.setCurrentIndex(tid)
                if mytype=='RF (freq)':
                    if not cid:
                        self.tek.RF_start_freq.setValue(myvalue)
                        self.tek.Change_RF_startF()
                    else:
                        self.tek.RF_stop_freq.setValue(myvalue)
                        self.tek.Change_RF_stopF()
                else:
                    self.tek.RF_amplitude.setValue(myvalue)
                    self.tek.Change_RF_amplitude()
            elif mytype=='EagleDAC':
                self.eagledac.Eagle_boxes[cid].setValue(myvalue)
            else:
                stages[tid].boxes[devind[mytype][cid]].setValue(myvalue)
        #self.pulse_off()
        QApplication.processEvents()
        
        self.GoAction(check_trap = True)
        #self.loadData()
        #self.MOTTimer.stop()
        ##self.pulse_off()
        #self.doGo(check_trap = True)
        
        
        #self.updateDC()
        #self.pulse_on()
        #self.MOTTimer.start(round(self.fluo_sampletime*1000))
        #QApplication.processEvents()
        
        if self.MOTfull_flag:
            filename=f'{self.datapath}/{mydate}/Data_{str(i)}.fit'
            self.parent().mysave(filename)
        else:
            t_f = time.perf_counter()  
            print(f'MultiGo failed due to lack of atoms during experiment {i+1}, having reached the end of the {self.fluo_timeout}s time-out. It had been running for {t_f-t_i:.3f} seconds.')
            break
            
        if self.MGinterrupt:
            self.MGinterrupt=False
            t_f = time.perf_counter()  
            print(f'MultiGo was stopped at the end of experiment {i+1}, having worked for {t_f-t_i:.3f} seconds.')
            break
        #wait(10)#time.sleep(10)
        
      if i+1 == npts:
        self.MultiGoButton.setText('MultiGo')
        self.MultiGoButton.setChecked(False)
        t_f = time.perf_counter()  
        print(f'MultiGo successfully completed {npts} experiments in a time of {t_f-t_i:.3f} seconds.')
    #==============================================================================================================
    #==============================================================================================================

    def TimerChange(self):
      if self.cbMOTLoad.checkState():
        self.pulse_on()
        #self.MOTTimer.start(round(self.fluo_sampletime*1000))
      else:
        self.pulse_off()
        #self.MOTTimer.stop()
        
    def makeFluoFig(self):
        self.fluo_plottime = 10#seconds
        fig = self.figure_fluo
        fig.clf()
        ax1 = fig.add_subplot()
        ax1.set_autoscaley_on(True)
        ax1.set_xlim(-self.fluo_plottime,0)

        color = 'tab:red'
        ax1.set_xlabel('time (s)')
        ax1.set_ylabel('PDiode', color=color)
        #ax1.plot(t, data1, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        self.colorpdiode = color

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        ax2.set_autoscaley_on(True)
        ax2.set_xlim(-self.fluo_plottime,0)

        color = 'tab:blue'
        ax2.set_ylabel('BF Cam', color=color)  # we already handled the x-label with ax1
        #ax2.plot(t, data2, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        self.colorbfcam = color

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        
        #self.fluofig = [fig, ax1, ax2]
        self.fluo_pdiode = []
        self.fluo_bfcam = []
        
        self.figure_fluoaxes = [ax1,ax2]
        
        #plt.show()
        #plt.pause(0.001)
        
    def plotBlackfly(self):
        fig = self.figure_blackfly
        fig.clf()
        ax = fig.add_subplot()
        
        bf = self.parent().bfcam
        # need mydiff, height, wx, wy, contourdata
        plt.ion()
            
        N_atoms = bf.Natoms[-1]
        height, wx, wy, contourdata = bf.fitparams
        
        #fig = plt.figure()
        #plt.imshow(mydiff, cmap = cm.inferno)
        #plt.colorbar()
        ax.imshow(mydiff,cmap = cm.inferno)
        
        
        if bf.fitsuccess:#self.fitflag and fitsuccess:
            try:
              prefix = ''
              #height,wx,wy, contourdata=self.gaussfit(mydiff, contourflag=True) # assuming already done to produce fitsuccess=True
              
              # For gaussian, assume particle number ~ int Gauss dx dy = w_x * w_y * height
              if N_atoms:
                if N_atoms < 0:
                  print(f'N_atoms = {N_atoms} < 0; using Gaussian fit instead\n(N_atoms = h * w_x * w_y)')
                  try:
                    N_atoms = height*wx*wy
                    widthtext = f'{roundstr(wx,0)}x, {roundstr(wy,0)}y;'
                  except:
                    N_atoms = 0
                    widthtext = 'Fits failed: 0x, 0y;'
                  
                if N_atoms > 0:
                  power = np.floor(np.log10(N_atoms)/3)
                  N_est = roundstr(N_atoms*10**(-3*power),1)
                  try:
                    widthtext = f'{roundstr(wx,0)}x, {roundstr(wy,0)}y;'
                  except:
                    widthtext = 'Fits failed: 0x, 0y;'
                  print(f'N of Atoms: {N_est} x 10^{int(3*power)}')
                else:
                  print('Gaussian fit also failed; setting N_atoms = 0')
                  N_est = 0; power = 0
                  widthtext = 'Fits failed: 0x, 0y;'
              else:
                try:
                  power = 1
                  N_est = roundstr(wx*wy*height/1000,0)
                  widthtext = f'{roundstr(wx,0)}x, {roundstr(wy,0)}y;'
                except:
                  N_est = 0; power = 0
                  widthtext = 'Fits failed: 0x, 0y;'
              ax.set_title(f"{widthtext} N_est = {N_est}x10^{int(3*power)}")#,roundstr(wy*py[0]/1000,0)))
            except Exception as e:
                ax.set_title=(f"Fits failed; Exception: {e}")
        else:
            if N_atoms > 0:
                power = np.floor(np.log10(N_atoms)/3)
                N_est = roundstr(N_atoms*10**(-3*power),1)
                print(f'N of Atoms: {N_est} x 10^{int(3*power)}')
            print('Gaussian fits currently disabled - see \'self.fitflag\' in blackfly.py')
            
        if contourdata and bf.contourflag:
          print('Plotting contours...')
          ax.contour(contourdata[0][0],contourdata[0][1], contourdata[1], 8)
          
        ax.set_xlabel('X (pixels)')
        ax.set_ylabel('Y (pixels)')
        bf.OD_fig = fig
        
        self.canvas_blackfly.draw_idle()
        #plt.draw() # Apparently this is preferred over show() for gui applications
        #plt.show()
        #plt.pause(0.001)
        

        # Make data.
        #X = np.arange(-5, 5, 0.25)
        #Y = np.arange(-5, 5, 0.25)
        #X, Y = np.meshgrid(X, Y)
        #R = np.sqrt(X**2 + Y**2)
        #Z = np.sin(R)

        # Plot the surface.
        #if self.surf_flag:
        #    ax = plt.figure().add_subplot(projection='3d')
        #    surf = ax.plot_surface(contourdata[0][0],contourdata[0][1], mydiff, cmap=cm.coolwarm,
        #                          linewidth=0, antialiased=False)
        #    ax.contour(contourdata[0][0],contourdata[0][1], contourdata[1], 8)
        #    plt.colorbar(surf, shrink=0.5, aspect=5)
        # 
        #     #plt.draw() # Apparently this is preferred over show() for gui applications
        #     plt.show()
        
    def plotFluo(self):
        plt.ion()
        #fig = self.fluofig[0]
        #axes = self.fluofig[1:]
        axes = self.figure_fluoaxes
        
        x = np.linspace((1-len(self.fluo_pdiode))*self.fluo_sampletime, 0,len(self.fluo_pdiode))
        
        colors = [self.colorpdiode, self.colorbfcam]
        data = [self.fluo_pdiode]
        if self.fluo_mode=='bfcam':
            data.append(self.fluo_bfcam)
        else:
            data.append(np.zeros(len(self.fluo_pdiode)))
        
        
        for i,ax in enumerate(axes):
            #if ax.lines:
            #
            #    ax.lines[0].set_xdata(x)
            #    ax.lines[0].set_ydata(data[i])
            #    ax.relim()
            #    ax.autoscale_view()
            #    
            #    fig.canvas.draw()
            #    fig.canvas.flush_events()
            #else:
            #     ax.plot(x,data[i],colors[i])
            ax.relim()
            ax.autoscale_view()
            ax.plot(x, data[i], colors[i])
        self.canvas_fluo.draw_idle()
        #plt.pause(0.001)
        

    def MOTTimerAction(self):
          self.fluorescence = 0
          self.t_final = time.time()
          self.fluo_nsamples = int(self.fluo_plottime/self.fluo_sampletime)
          
          fluo_pdiode=self.adc.read(0)
          self.fluo_pdiode.append(fluo_pdiode)
          while len(self.fluo_pdiode)>self.fluo_nsamples:
            del self.fluo_pdiode[0]
          
          if self.fluo_mode == 'bfcam' and hasattr(self.parent(),'bfcam'):
            self.fluorescence = self.parent().bfcam.req_fluo()
            self.fluo_bfcam.append(self.fluorescence)
            while len(self.fluo_bfcam)>self.fluo_nsamples:
              del self.fluo_bfcam[0]
          else:
            self.fluorescence = fluo_pdiode
          
          self.plotFluo()#self.fluofig[1:])
          
          self.fluo.display(self.fluorescence)
          self.MOTfull_flag=False
          if self.fluorescence - self.fluo_zero > self.fluo_percentage * (self.fluo_max - self.fluo_zero): #400 :
            self.MOTfull_flag = True
            #plt.close('all')
            if self.MG_active:
              print(f'Reached net fluorescence of {self.fluorescence - self.fluo_zero}, exceeding required {self.fluo_percentage * (self.fluo_max - self.fluo_zero)}\n'
                    f'Reached in a time of {self.t_final - self.t_initial:.1f} seconds')
              self.MG_MOTfull_action()
            elif self.ML_active:
              print(f'Reached net fluorescence of {self.fluorescence - self.fluo_zero}, exceeding required {self.fluo_percentage * (self.fluo_max - self.fluo_zero)}\n'
                    f'Reached in a time of {self.t_final - self.t_initial:.1f} seconds')
              self.ML_MOTfull_action()
          if (self.t_final - self.t_initial > self.fluo_timeout):
            if self.MG_active:
              print(f'Fluorescence timeout exceeded! (Waited {self.t_final - self.t_initial:.1f} seconds, surpassing timeout at {self.fluo_timeout} seconds.')
              self.MG_active = False
            if self.ML_active:
              print(f'Fluorescence timeout exceeded! (Waited {self.t_final - self.t_initial:.1f} seconds, surpassing timeout at {self.fluo_timeout} seconds.')
              self.ML_active = False
         #if self.MG_active and self.MOTfull_flag:
          #  self.MG_MOTfull_action()
          
            
          
    def pulse_on(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml='PULSE,ON'
        s.send(ml.encode())
        #s.recv(5)
        s.close()
        wait(0.1)#time.sleep(0.1)

    def pulse_off(self, dontclose=False):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml='PULSE,OFF'
        s.send(ml.encode())
        #s.recv(5)
        if dontclose:
          return s
        else:
          s.close()
          wait(0.1)#time.sleep(0.1)
        
#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================
#class StagePushButton(QPushButton):
#    def __init__(self):
#        super(QPushButton,self).__init__(name)
    
        
        


class StageLabel(QPushButton):
    def __init__(self, name,notes="",parent=None):
        QPushButton.__init__(self,parent)
        #self.btn=QPushButton(name,self)
        self.setText(name)
        self.notes=notes
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
    #def mousePressEvent(self,event):
        ##print("Mhouse pressed")
        #if event.button()==Qt.LeftButton:
          #self.thisbutton=True
          ##print("Leffbutton")
        #else:
          #self.thisbutton=False
        ##self.emit(clicked)
        #return QWidget.mousePressEvent(self,event)
        
        
class LabelDialog(QDialog):
    def __init__(self,name,notes):
          super(QDialog, self).__init__()
          self.setWindowTitle("Adjusting stage '"+name+"'")
          self.layout = QGridLayout()
          self.namebox=QLineEdit()
          self.namebox.setText(name)
          self.layout.addWidget(QLabel("Stage name:"),0,0)
          self.layout.addWidget(self.namebox,0,1)
          
          self.notesbox=QPlainTextEdit()
          self.notesbox.clear()
          self.notesbox.insertPlainText(notes)
          self.layout.addWidget(QLabel("Notes:"),1,0)
          self.layout.addWidget(self.notesbox,1,1)
          QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
          self.buttonBox = QDialogButtonBox(QBtn)
          self.buttonBox.accepted.connect(self.naccept)
          self.buttonBox.rejected.connect(self.reject)
          self.layout.addWidget(self.buttonBox,2,0)
          self.setLayout(self.layout)
    def naccept(self):
          self.accept()
    def reject(self):
          self.close()
          
class FluoDialog(QDialog):
    def __init__(self, zero, maxval, threshold_percentage, timeout, sampletime, adc):#filename,devnames,stagenames, tek):
        super(QDialog, self).__init__()
        self.setWindowTitle("Fluorescence Settings")
        self.layout = QGridLayout()
        
        self.adc = adc
        self.fluorescence = self.get_current_fluo()
        
        self.values = [zero, maxval, threshold_percentage, timeout, sampletime]
        
        self.mins = [0.01,0.01,0.01, 1, 0.05]
        self.maxes = [9999.9,9999.9,1,120,10]
        self.decimals = [2,2,2,0,2]
        self.units = ['a.u.', 'a.u.', '', 's', 's']
          
        self.layout = QGridLayout()
        self.make_dialog()
        
    def get_current_fluo(self):
        return self.adc.read(0)
        
    def make_dialog(self):
        explain_label=QLabel('Heres how this works')
        self.layout.addWidget(explain_label,0,0)
        
        labs = [f'Background reading (<{self.maxes[0]})','Full MOT reading (<{self.maxes[1]})','Threshold % ({self.mins[2]} - {self.maxes[2]})',\
          'Timeout (<{self.maxes[3]}{self.units[3]})', 'Sampling time (<{self.maxes[4]}{self.units[4]})']
        
        self.labels=[]
        self.boxes=[]
        self.useFluoButton=[]
        for i, rlab in enumerate(labs):
            sidelab=QLabel(rlab)
            self.labels.append(sidelab)
            self.layout.addWidget(self.labels[-1],i+1,0)

            self.boxes.append(QDoubleSpinBox())
            self.boxes[-1].setRange(self.mins[i],self.maxes[i])
            self.boxes[-1].setDecimals(self.decimals[i])
            self.boxes[-1].setSingleStep(self.mins[i])
            self.boxes[-1].setToolTip(f'Allowed range: {str(self.mins[i])} -> {str(self.maxes[i])}{self.units[i]}')
            self.boxes[-1].setValue(self.values[i])
            if i<3:
                self.boxes[-1].valueChanged.connect(self.setThresholdText)
            self.layout.addWidget(self.boxes[-1],i+1,1)
            
            if i==2:
                self.thresholdLabel = QLabel('Threshold Fluo.: N/A')
                self.layout.addWidget(self.thresholdLabel,i+1,2)
            
            if i<2:
                self.useFluoButton.append(QPushButton('Use current fluo.'))
                self.useFluoButton[-1].clicked.connect(partial(self.currentFluorescenceAction, i))
                self.layout.addWidget(self.useFluoButton[-1],i+1,2)
        
        self.setThresholdText()
        
        self.setValsButton = QPushButton('Set Values')
        self.setValsButton.clicked.connect(self.changeValues)
        self.layout.addWidget(self.setValsButton,len(self.values)+1,0)
        
        self.setLayout(self.layout)
        
    def currentFluorescenceAction(self,i):
        fluo = self.get_current_fluo()
        self.boxes[i].setValue(fluo)
        
    def setThresholdText(self):
        threshold_value = self.boxes[0].value() + self.boxes[2].value() * (self.boxes[1].value() - self.boxes[0].value())
        self.thresholdLabel.setText(f'Threshold Fluo.:{threshold_value:.1f}')
        
    def changeValues(self):
        self.values = [box.value() for box in self.boxes]
        self.accept()#return [box.value() for box in self.boxes] 
        

          
#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================

def wait(maxtime, t_gap = 0.05): # note: maxtime should really be >> tgap or you might wait longer than you need to for the delay to end
    t_init = time.time()
    t_final = time.time()
    while t_final - t_init < maxtime:
        QApplication.processEvents()
        time.sleep(t_gap) # in seconds
        t_final = time.time()

if __name__=='__main__':
  npts=100000
  da.GetDevices()
  import time
  while (1):
    da.DACDirect(0,3,4095)
    wait(1)#time.sleep(1)
    da.DACDirect(0,3,0)
    wait(1)#time.sleep(1)
