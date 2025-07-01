# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""


from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import astropy.io.fits as fits
import numpy as np
from qmsbox import *
from dacprops import *
import camera_test
import tek_afg as afg
#import DAQ
import time
import matplotlib.pyplot as plt
import Stages as stg
from functools import partial
#try:
import EagleDAC_main as eagle
import adclib
#except:
#    pass
from datetime import datetime
import os
import glob
import multigo_window as mg

#import socket
#TCP_IP = '130.216.51.179'
#TCP_PORT = 8833
#BUFFER_SIZE = 50
datapath='/home/lab/mydata/Data/'
MAX_INT=0xfff

#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================

class allboxes(QWidget):
    def __init__(self, tables, parent=None):#ndacs,naoms,ntimes):
      super(allboxes, self).__init__(parent=parent)
      try:
          print(da.GetDevices()) # This is required for all apps using the DAC
      except:
          print("DA not present")
          self.DApresent=False
          
      # Label data from save-file appropriately so that it can be 
      #         loaded into relevant boxes when the window is populated     
      self.tableinit,self.curvesinit,self.eagledata,\
        self.DIOinit,self.RFinit, self.MGinit,\
          names, self.notes, headers = tables
      
      # Initialising layout
      self.layout = QGridLayout(self)
      self.layout.setSpacing(1)
      
      self.hlines=1 # Should allow us to add extra stuff to the top of the window without issue
      
      # ALL NAMES HERE LOADED IN BY IMPORTING 'daqprops.py'
      # We just store the names in a usable state here
      self.aomlist = [AOM+suffix for AOM in aom_names for suffix in [' Freq',' Ampl']]
      self.DIOnames=['RF Ramp Trigger','Unused']
      self.devicenames={'DAC':dac_names, 'DIO':self.DIOnames, 'AOM':self.aomlist,'EagleDAC':EDnames}
      
      # Initialise stage boxes and load data into them from save-file values.
      #         See 'Stages.py' for more detail
      self.Stages=stg.Stages(devdict=self.devicenames, stagenames=names,table=self.tableinit, curves=self.curvesinit, DIOstate=self.DIOinit)
      self.nstages=len(self.Stages.stages)
      if not self.notes:
        self.notes = ["" for i in range(self.nstages)]
      
      # Now we create/place the relevant widgets for everything, and finalise the layout
      self.remakeWindow(initial=True)
      self.setLayout(self.layout)
      
      # We're going to store a set of background pics to use for fringe removal
      self.BGimages=[[] for i in range(50)]
      # We also store the number of times images have been stored here
      self.nBGstored=0
      
      try:
          self.adc=adclib.adc()
      except:
          pass

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
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -     
      # We're gonna reconstruct the 'stage label' pushbuttons at the top of the screen
      # Honestly, aside from re-adding the buttons to the layout, I'm not sure whether this is necessary
      
      # First, we make absolutely sure we've removed them all
        if not initial:
          for i in range(len(self.stagelabels)):
            self.stagelabels[-1].btn.deleteLater()
            self.stagelabels[-1].deleteLater()
            del self.stagelabels[-1]

        self.stagelabels=[StageLabel(stage.name) for stage in stge.stages]
        
        if not self.notes:
          self.notes=[""]*self.nstages
        elif len(self.notes)<self.nstages:
          self.notes+=[""]*(self.nstages - len(self.notes))
        for i in range(self.nstages):
          self.stagelabels[i].notes = self.notes[i]
          self.stagelabels[i].btn.clicked.connect(partial(self.changetextnotes,i))
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      # Ok, NOW we the stage labels and associated timeboxes to the top of the window
        for stgID,stage in enumerate(stge.stages):
          # Note column placement is 'stage ID + 2';
          #     + 2 -> First two columns are DC values and device labels
          self.layout.addWidget(self.stagelabels[stgID].btn,0,stgID+2) 
          self.layout.addWidget(stage.time, 1, stgID+2)
      # and for each stage, we add all associated device boxes
          for boxID,box in enumerate(stage.boxes):
            # Similarly, + 2 -> First two rows are stage labels and associated times
            self.layout.addWidget(box, boxID+2, stgID+2)
      # Here endeth the creation of the main set of interactive boxes
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # The other thematic groups of buttons/boxes have their own loading functions below
      # We feed in the parameter 'initial' (only =True on start-up, in theory)
      # If initial = True, we create and load in data.
      # If False, we just remake the widgets.
        self.makeRFwindow(initial)
        self.makeEDACwindow(initial)
        self.makeGOLOADbuttons(initial)
        self.makeMGwindow(initial)
        self.makeStageButtons(initial)
        
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
          print(f'Stage added at position {pos}!')
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
          print(f'Stage {pos} duplicated and placed at position {target}!')
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
          print(f'Stage {pos} moved to position {target}!')
        else:
          print("You must select an appropriate adjustment proceed!")
      
    def setStageChangeBoxes(self,kind):
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
            
    def makeRFwindow(self,initial=False):
      if initial:
        self.tek=afg.TekAFG()
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
      self.layout.addWidget(self.tek,self.hlines+40,0,2,5) 
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    def makeEDACwindow(self,initial=False):
      if initial:
        self.eagledac=eagle.EaglePanel()
        for i in range(24):
          self.eagledac.Eagle_boxes[i].setToolTip(EDnames[i])
          try:
            self.eagledac.Eagle_boxes[i].setValue(self.eagledata[i][0])
          except:
            self.eagledac.Eagle_boxes[i].setValue(0)
      self.layout.addWidget(self.eagledac,self.hlines+42,0,4,5)
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    def makeMGwindow(self,initial=False):
      if initial:
        self.MGPanel=mg.MultiGoPanel()
        self.MultiGoButton=QPushButton('MultiGo')
        self.MultiGoButton.clicked.connect(self.MultiGo)
        self.MGParamButton=QPushButton('Parameters')
        self.MGParamButton.clicked.connect(self.mgmenu)
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
      
      self.layout.addWidget(self.MGPanel,self.hlines+40,7,5,2)
      self.layout.addWidget(self.MultiGoButton,self.hlines+45,7)
      self.layout.addWidget(self.MGParamButton,self.hlines+45,8)
      
    def makeStageButtons(self,initial=False):
      if initial:
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
      
      self.layout.addWidget(self.stagechangetypebutton,self.hlines+40,5)
      self.layout.addWidget(self.combostagechange,self.hlines+40,6)
      self.layout.addWidget(self.stagetargetlabel,self.hlines+41,5)
      self.layout.addWidget(self.combostagetarget,self.hlines+41,6)
      self.layout.addWidget(self.stageposlabel,self.hlines+42,5)
      self.layout.addWidget(self.combostagepos,self.hlines+42,6)
      
    def stageboxaction(self):
      self.setStageChangeBoxes(self.combostagechange.currentText())
    
    def makeGOLOADbuttons(self,initial=False):
      if initial:
        self.GoButton=QPushButton('Go')
        self.GoButton.clicked.connect(self.GoAction)
        self.CycleButton=QPushButton('Cycle')
        self.CycleButton.clicked.connect(self.CycleAction)
        self.cbPictype=QComboBox()
        for label in ["No picture","One shot","Fluorescence","Shadow image"]: self.cbPictype.addItem(label)
        self.camera=camera_test.camera()
        self.cycling=False
        self.cbMOTLoad=QCheckBox()
        self.cbMOTLoad.stateChanged.connect(self.TimerChange)
        self.MOTLoadLabel=QLabel('Load MOT')
        self.MOTTimer=QTimer(self)
        self.MOTTimer.timeout.connect(self.MOTTimerAction)
        self.fluo=QLCDNumber()
        
      self.layout.addWidget(self.fluo,self.hlines+45,6)
      self.layout.addWidget(self.GoButton,self.hlines+44,5)
      self.layout.addWidget(self.CycleButton,self.hlines+45,5)
      self.layout.addWidget(self.cbPictype,self.hlines+44,6)
      self.layout.addWidget(self.cbMOTLoad,self.hlines+43,6,alignment=Qt.AlignCenter)
      self.layout.addWidget(self.MOTLoadLabel,self.hlines+43,5)
    
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
                time.sleep(0.1)
            elif isinstance(DCbox, DC_AOM_Freq_Box) or isinstance(DCbox, DC_AOM_Ampl_Box):
                DCbox.update()
                time.sleep(0.1)

    #==============================================================================================================
    #==============================================================================================================
        
    def changetextnotes(self,i):
        label=self.stagelabels[i]
        dialog = LabelDialog(label.btn.text(),label.notes)
        if dialog.exec_():
          newname=dialog.namebox.text()
          self.Stages.stages[i].name=newname
          label.btn.setText(newname)
          label.notes=dialog.notesbox.toPlainText()
          self.notes[i]=label.notes
          self.remakeWindow()

    #==============================================================================================================
    #==============================================================================================================

    def loadData(self):
        
        stages=self.Stages.stages
        devIDs = self.Stages.devIDs
        self.totaltime=0.0
        self.timestep=0.05/(1.0+0.0625e-3)
        self.totaltime=sum([stage.time.value() for stage in stages])
        nsteps=int(self.totaltime/self.timestep + 1) # assuming timesteps of 0.1 ms

        data=np.zeros([nsteps,len(self.devicenames['DAC'])])
        timestepstilnow=0
        thetime=0.0
        msg='LOAD,'
        msg2='LOAD,'
        for tid in range(len(stages)):
            timesteps=int(stages[tid].time.value()/self.timestep)
            for t in range(timesteps):
                i = t + timestepstilnow
                for row in range(len(self.devicenames['DAC'])):
                    temp=stages[tid].boxes[row].value()
                    if ((temp>=0.0) and (temp<=5.0)):
                        data[i,row]=int(temp*MAX_INT/5.0)
                    elif (temp==-20.0):
                        tmp2=stages[tid].boxes[row].LOffset+stages[tid].boxes[row].LAmp/(1.0+(t*self.timestep/stages[tid].boxes[row].LTc)**2)
                        data[i,row]=int(tmp2*MAX_INT/5.0)
                    elif (temp==-30.0):
                        tmp2=stages[tid].boxes[row].RStart+t*(stages[tid].boxes[row].REnd-stages[tid].boxes[row].RStart)/timesteps
                        data[i,row]=int(tmp2*MAX_INT/5.0)
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
                        
                    temp=stages[tid].boxes[t1+1].value()
                    if round(100*(temp-self.Stages.DC[t1+1].value()))!=0: # Be aware - fstring formatting is to force 2dp rounding so that DDS doesnt get upset
                        msg=msg+str(t2)+','+'AMPL,'+str(AOM)+','+f'{temp:.2f}'+','#str(temp)+','
                else:
                    temp=stages[tid].boxes[t1].value()
                    if round(temp-stages[tid-1].boxes[t1].value())!=0:
                        msg=msg+str(time_aom+AOM)+','+'FREQ,'+str(AOM)+','+str(temp)+','
                    temp=stages[tid].boxes[t1+1].value()
                    if round(100*(temp-stages[tid-1].boxes[t1+1].value()))!=0: # Be aware - fstring formatting is to force 2dp rounding so that DDS doesnt get upset
                        msg=msg+str(time_aom+AOM)+','+'AMPL,'+str(AOM)+','+f'{temp:.2f}'+','#str(temp)+','
              
              for num,DIOid in enumerate(devIDs['DIO']):
                if tid==0:
                    t1=self.Stages.DC[DIOid].isChecked()
                else:
                    t1=stages[tid-1].boxes[DIOid].isChecked()
                t2=stages[tid].boxes[DIOid].isChecked()
                if (t1 != t2):
                    msg=msg+str(time_aom+14+num)+",TRIG,"+str(num)+','+str(int(t2))+','
                    
            if len(self.devicenames['AOM'])>8:
              n2=int(len(self.devicenames['AOM'])/2) - 4
              for AOM in range(n2): # Same for second AOM
                #t1=2*AOM+self.nDACs+8
                t1=devIDs['AOM'][2*AOM+8]
                if tid==0:
                    temp=stages[tid].boxes[t1].value()
                    print(temp,t1,stages[tid].boxes[t1].value())
                    if round(temp-self.Stages.DC[t1].value())!=0:
                        msg2=msg2+'10,'+'FREQ,'+str(AOM)+','+f'{temp:.0f}'+','
                    temp=stages[tid].boxes[t1+1].value()
                    if round(100*(temp-self.Stages.DC[t1+1].value()))!=0:
                        msg2=msg2+'10,'+'AMPL,'+str(AOM)+','+f'{temp:.2f}'+','
                else:
                    temp=stages[tid].boxes[t1].value()
                    if round(temp-stages[tid-1].boxes[t1].value())!=0:
                        msg2=msg2+str(time_aom)+','+'FREQ,'+str(AOM)+','+f'{temp:.0f}'+','
                    temp=stages[tid].boxes[t1+1].value()
                    if round(100*(temp-stages[tid-1].boxes[t1+1].value()))!=0:
                        msg2=msg2+str(time_aom)+','+'AMPL,'+str(AOM)+','+f'{temp:.2f}'+','        
            thetime=thetime+stages[tid].time.value()
        msg=msg+"F"
        msg2=msg2+"F"
        if (len(msg)>6):
            print(msg)
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send(msg.encode())
            print(s.recv(5))
            s.close()
        if (len(msg2)>6):
            print(msg2)
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP2, TCP_PORT))
            s.send(msg2.encode())
            s.recv(5)
            s.close()
        self.nsamples=timestepstilnow

    #==============================================================================================================
    #==============================================================================================================

    def GoAction(self):
        self.loadData()
        self.MOTTimer.stop()
        self.pulse_off()
        self.doGo()
        self.updateDC()
        time.sleep(0.1)
        if self.cbMOTLoad.isChecked():
          self.MOTTimer.start(100)
          self.pulse_on()
          
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
                    
    def doGo(self):
        nshots=self.cbPictype.currentIndex()
        plt.close()
        if (nshots>0):
            if self.parent().blackfly_action.isChecked():
              self.parent().bfcam.shoot(nshots)
              #a=1
            if self.parent().princeton_action.isChecked():
              self.camera.shoot(nshots)
        msg='EXPT'
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(msg.encode())
        print(s.recv(5))
        s.close()
        time.sleep(0.01)
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(self.devicenames['AOM'])>8:
            s.connect((TCP_IP2, TCP_PORT))
            s.send(msg.encode())
            a=s.recv(5)
            print(a)
            s.close()
        time.sleep(0.01)
        nsamples=self.data.shape[0]
        data = self.data.flatten('C').astype(np.ushort)
        datalen=data.shape[0]
        if (datalen<=0x10001) :
            firstval=data[0]+0x1000
            data2=np.ones(0x10001,dtype=np.ushort)*firstval
            data2[0:datalen]=data[:]
            data=data2
        data[datalen-1]+=0x8000
        datalen=data.shape[0]
        freq=20000

        result=da.DACOutputProcess(0,freq,datalen,data)
        time.sleep(1)

        if (nshots>0):
            if self.parent().blackfly_action.isChecked():
              #self.parent().bfcam.shoot(nshots)
              print(self.BGimages)
              self.BGimages = self.parent().bfcam.show(nshots,self.BGimages,self.nBGstored)
              self.nBGstored+=1
            if self.parent().princeton_action.isChecked():
              self.camera.shoot(nshots)
              self.mydata=self.camera.read()
              plt.imshow(self.mydata)
              plt.show()
        f=open('test.txt','w')
        for i in range(self.data.shape[0]):
          for j in range(self.data.shape[1]):
            f.write("%d \n" % self.data[i,j])
        f.close()
        
    #==============================================================================================================
    #==============================================================================================================
          
    def mgmenu(self):
        currentindex=self.MGPanel.cbExpKind.currentIndex()
        mg.multigomenu(self.MGPanel,self.devicenames,[self.Stages.stages[i].name for i in range(self.nstages)])
        self.fill_MG_files()
        self.MGPanel.cbExpKind.setCurrentIndex(currentindex) # returns to previous parameter set, rather than new one!

    def fill_MG_files(self):
        self.MGPanel.cbExpKind.clear()
        flist=sorted(glob.glob("*.mgo"))
        for item in flist:
          sitem=item[:-4]
          self.MGPanel.cbExpKind.addItem(sitem)
    
    def MultiGo(self):
       stages=self.Stages.stages
       devind = self.Stages.devIDs
       self.MOTTimer.stop()
       self.pulse_off()
       eid=self.MGPanel.cbExpKind.currentIndex()
       npts=self.MGPanel.sbNCycles.value()
       #if eid<3:
       #  b_val=self.MGPanel.sbExpFrom.value()
       #  e_val=self.MGPanel.sbExpTo.value()
       #  dacid=self.MGPanel.cbExpKind.currentIndex()+3
       #else:
       fname=self.MGPanel.cbExpKind.currentText()+'.mgo'
       mgpars = mg.Parameters(self.devicenames,self.stagenames)
       mgpars.newread(fname)
       #self.eagledac.Eagle_boxes[dacid].setPalette(QPalette)
       mydate=datetime.now().strftime('%Y%m%d%H%M')
       os.mkdir(datapath+'/'+mydate)
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
                if not mytype=='RF (freq)':
                    myvalue=b_val+i*(e_val-b_val)/(npts-1)
                else:
                    myvalue=b_val+i*(e_val-b_val)/(npts)
                    nextval=b_val+(i+1)*(e_val-b_val)/(npts)
            else:
                myvalue=b_val
            if not mytype=='EagleDAC':
                tid=p.time.currentIndex()
            if not mytype=='Time' and not mytype=='RF':
                cid=p.channel.currentIndex()
            if mytype=='Time':
                stages[tid].time.setValue(myvalue)
            elif mytype=='RF (freq)' or mytype=='RF (amp)':
                     #self.tek.Change_RF_length(self.Timeboxes[tid].value()) # Not necessary, I think; should be changed automatically when RF stage select adjusts stage ID.
                rfdisnum=[j for j, x in enumerate(self.Stages.devices['DAC']) if x=='RF disable']
                rfdisableind = devind['DAC'][rfdisnum[0]]
                rfdioind = devind['DIO'][0]
                stages[tid].boxes[rfdisableind].setValue(0.0)
                for j in range(len(stages)):
                    stages[j].boxes[rfdioind].setChecked(False)
                stages[tid].boxes[rfdioind].setChecked(True)
                self.tek.RF_stage_select.setCurrentIndex(tid)
                if mytype=='RF (freq)':
                    self.tek.RF_start_freq.setValue(myvalue)
                    self.tek.Change_RF_startF()
                    self.tek.RF_stop_freq.setValue(nextval)
                    self.tek.Change_RF_stopF()
                else:
                    self.tek.RF_amplitude.setValue(myvalue)
                    self.tek.Change_RF_amplitude()
            elif mytype=='EagleDAC':
                self.eagledac.Eagle_boxes[cid].setValue(myvalue)
            else:
                stages[tid].boxes[devind[mytype][cid]].setValue(myvalue)
         self.pulse_off()
         QApplication.processEvents()
         self.loadData()
         self.doGo()
         filename=datapath+'/'+mydate+'/Data_'+str(i)+'.fit'
         self.parent().mysave(filename)
         self.updateDC()
         self.pulse_on()
         time.sleep(10)
         
    #==============================================================================================================
    #==============================================================================================================

    def TimerChange(self):
      if self.cbMOTLoad.checkState():
        self.pulse_on()
        self.MOTTimer.start(100)
      else:
        self.pulse_off()
        self.MOTTimer.stop()

    def MOTTimerAction(self):
          self.fluo.display(self.adc.read(0))
          
    def pulse_on(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml='PULSE,ON'
        s.send(ml.encode())
        s.recv(5)
        s.close()

    def pulse_off(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml='PULSE,OFF'
        s.send(ml.encode())
        s.recv(5)
        s.close()
        
#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================

class StageLabel(QPushButton):
    def __init__(self, name,notes="",parent=None):
        QPushButton.__init__(self,parent)
        self.btn=QPushButton(name,self)
        self.btn.setText(name)
        self.notes=notes
        
        
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
          
#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================


if __name__=='__main__':
  npts=100000
  da.GetDevices()
  import time
  while (1):
    da.DACDirect(0,3,4095)
    time.sleep(1)
    da.DACDirect(0,3,0)
    time.sleep(1)
