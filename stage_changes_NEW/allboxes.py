# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""


from PyQt5.QtCore import *
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
try:
    import EagleDAC_main as eagle
    import adclib
except:
    pass
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

class allboxes(QWidget):
    def __init__(self,tables):#ndacs,naoms,ntimes):
      super(allboxes, self).__init__()
      try:
          print(da.GetDevices()) # This is required for all apps using the DAC
      except:
          print("DA not present")
          self.DApresent=False
          
      self.tableinit,self.curvesinit,self.eagledata,self.DIOinit,self.RFinit, self.MGinit = tables
      
      self.layout = QGridLayout(self)
      self.layout.setSpacing(1)
      
      self.aomlist = [AOM+suffix for AOM in aom_names for suffix in [' Freq' ' Ampl']]
      self.DIOnames=['RF Ramp Trigger','Unused']
      self.devicenames={'DAC':dac_names, 'DIO':self.DIOnames, 'AOM':self.aomlist,'EagleDAC':EDnames}
      
      self.Stages=stg.Stages(devdict=self.devicenames, self.tableinit, self.curvesinit, self.DIOinit)
      
      self.remakeWindow()
      self.setLayout(self.layout)
      
      try:
          self.adc=adclib.adc()
      except:
          pass
        
    def remakeWindow(self,initial=False):
        QObjectCleanupHandler().add(self.layout())
        self.layout=QGridLayout(self)
        self.layout.setSpacing(1)
        
        stg = self.Stages
        
        self.layout.addWidget(QLabel('DC Values'),1,0)
        for dc_box,dcID in enumerate(stg.DC):
          self.layout.addWidget(dc_box,dcID+2,0)
          
        devlabels=[QLabel('Time (ms)')]
        for key in self.devicenames.keys(): 
          for device in self.devicenames[key]:
            devlabels.append(QLabel(device))
        for label, labID in enumerate(devlabels):
          self.layout.addWidget(label, labID+1,1)
          
        self.stagelabels=[QLabel(stage.name) for stage in stg.stages]
        for stage,stgID in enumerate(stg.stages):
          self.layout.addWidget(self.stagelabels[stgID],0,stgID+2)
          self.layout.addWidget(stage.time, 1, stgID+2)
          for box, boxID in enumerate(stage.boxes):
            self.layout.addWidget(box, boxID+2, stgID+2)
        
        self.makeRFwindow(initial)#(self.RFinput)#where self.RFinput=[stopf,startf,amplitude]
        self.makeEDACwindow(initial)
        self.makeGOLOADbuttons(initial)
        self.makeMGwindow(initial)
    
    def DelCol(self,position='last'):
        if position = 'last':
          position=-1
        self.Stages.delStage(position)
        self.remakeWindow()

    def DupCol(self,a=-1,position='last'):
        if position = 'last':
          position=-1
        self.Stages.dupStage(a,position)
        self.remakeWindow

    def AddCol(self,time=0,vals=[],DIOstate=[],position='last'):
        if position = 'last':
          position=-1
        self.Stages.addStage(time,vals,DIOstate,position)
        self.remakeWindow
            
    def makeRFwindow(self,initial=False):
      if initial:
        self.tek=afg.TekAFG()
        stop_f,start_f,amp = self.RFinit[:3]
          
        self.tek.RF_stop_freq.setValue(stop_f)
        self.tek.RF_start_freq.setValue(start_f)
        self.tek.RF_amplitude.setValue(amp)
          
        self.loadRFStages()
        self.tek.RF_stage_select.currentIndexChanged.connect(self.change_RF_stage)
          
      self.layout.addWidget(self.tek,self.hlines+40,5,5,2)
      
    def makeEDACwindow(self,initial=False):
      if initial:
        self.eagledac=eagle.EaglePanel()
        for i in range(24):
            self.eagledac.Eagle_boxes[i].setValue(self.eagledata[i][0])
      self.layout.addWidget(self.eagledac,self.hlines+40,0,4,5)
      
    def makeMGwindow(self,initial=False):
      if initial:
        self.MGPanel=mg.MultiGoPanel()
        self.MultiGoButton=QPushButton('MultiGo')
        self.MultiGoButton.clicked.connect(self.MultiGo)
        self.MGParamButton=QPushButton('Parameters')
        self.MGParamButton.clicked.connect(self.mgmenu)
        self.fill_MG_files()
        self.MGPanel.sbExpFrom.value(),self.MGPanel.sbExpTo.value(),\
          self.MGPanel.cbExpKind.currentIndex, self.MGPanel.sbNCycles.value() = self.MGinit
      
      self.layout.addWidget(self.MGPanel,self.hlines+40,7,5,2)
      self.layout.addWidget(self.MultiGoButton,self.hlines+45,7)
      self.layout.addWidget(self.MGParamButton,self.hlines+45,8)
      
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
      
      self.layout.addWidget(self.GoButton,self.hlines+44,1)
      self.layout.addWidget(self.CycleButton,self.hlines+45,1)
      self.layout.addWidget(self.cbPictype,self.hlines+44,2)
      self.layout.addWidget(self.cbMOTLoad,self.hlines+44,0)
      self.layout.addWidget(self.MOTLoadLabel,self.hlines+45,0)
        
    def mgmenu(self):
        mg.multigomenu(self.MGPanel,self.devicenames,self.stagenames)
        self.fill_MG_files()
        
    def RF_MG_store(self):
        RF_data=[self.tek.RF_stop_freq.value(), self.tek.RF_start_freq.value(), \
          self.tek.RF_amplitude.value(), self.tek.RF_stage_select.currentIndex(), \
            self.tek.RF_sweepstyle.currentIndex()]
          
        MG_data = [self.MGPanel.sbExpFrom.value(),self.MGPanel.sbExpTo.value(),\
          self.MGPanel.cbExpKind.currentIndex, self.MGPanel.sbNCycles.value()]
        
    def RF_MG_load(self,RF_data, MG_data):
       self.tek.RF_stop_freq.value(), self.tek.RF_start_freq.value(), \
          self.tek.RF_amplitude.value(), self.tek.RF_stage_select.currentIndex(), \
            self.tek.RF_sweepstyle.currentIndex() = RF_data
        
        self.MGPanel.sbExpFrom.value(),self.MGPanel.sbExpTo.value(),\
          self.MGPanel.cbExpKind.currentIndex, self.MGPanel.sbNCycles.value() = MG_data
        
    def loadRFStages(self):
        self.tek.RF_stage_select.clear()
        self.tek.RF_stage_select.addItems(self.stagenames)

    def which_RF_stage(self):
        name=self.tek.RF_stage_select.currentText()
        index = [i for i in range(len(self.Stages.stages)) if self.Stages.stages[i].name == name]
        assert len(index)==1; 'You have multiple stages sharing the same label - please give them all unique labels!'
        return index[0]

    def change_RF_stage(self,ind=-1):
        if ind<0:
          ind = self.which_RF_stage()
        newvalue=self.Stages.stages[ind].time.value()
        self.tek.Change_RF_stage(newvalue)
        self.RF_currentstage = ind
        
    def fill_MG_files(self):
        self.MGPanel.cbExpKind.clear()
        flist=sorted(glob.glob("*.mgo"))
        for item in flist:
          sitem=item[:-4]
          self.MGPanel.cbExpKind.addItem(sitem)

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


    def MultiGo(self):
       stages=self.Stages.stages
       devind = self.Stages.devIDs
       self.MOTTimer.stop()
       self.pulse_off()
       eid=self.MGPanel.cbExpKind.currentIndex()
       npts=self.MGPanel.sbNCycles.value()
       if eid<3:
         b_val=self.MGPanel.sbExpFrom.value()
         e_val=self.MGPanel.sbExpTo.value()
         dacid=self.MGPanel.cbExpKind.currentIndex()+3
       else:
         fname=self.MGPanel.cbExpKind.currentText()+'.mgo'
         mgpars = mg.Parameters(self.devicenames,self.stagenames)
         mgpars.newread(fname)
         print(mgpars.params)

       #self.eagledac.Eagle_boxes[dacid].setPalette(QPalette)
       mydate=datetime.now().strftime('%Y%m%d%H%M')
       os.mkdir(datapath+'/'+mydate)
       for i in range(npts):
         self.MGPanel.mgCount.setText(str(i+1)+' of '+str(npts))
         if (eid<3):
             myvalue=b_val+i*(e_val-b_val)/(npts-1)
             #print(myvalue)
             self.eagledac.Eagle_boxes[dacid].setValue(myvalue)
         else:
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
                     stage[tid].time.setValue(myvalue)
                 elif mytype=='RF (freq)' or mytype=='RF (amp)':
                     #self.tek.Change_RF_length(self.Timeboxes[tid].value()) # Not necessary, I think; should be changed automatically when RF stage select adjusts stage ID.
                     rfdisableind = devind['DAC'][i for i, x in enumerate(self.Stages.devices) if x=='RF disable']
                     rfdioind = devind['DIO'][0]
                     stage[tid].boxes[rfdisableind].setValue(0.0)
                     for i in range(len(stages)):
                         stages[i].boxes[rfdioind].setChecked(False)
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

    def updateDC(self):
        for DCbox in self.Stages.DC:
            if isinstance(DCbox, DC_DAC_Box):
                DCbox.updateDAC()
            elif isinstance(DCbox, DC_AOM_Freq_Box) or isinstance(DCbox, DC_AOM_Ampl_Box):
                DCbox.update()

    def TimerChange(self):
      if self.cbMOTLoad.checkState():
        self.pulse_on()
        self.MOTTimer.start(100)
      else:
        self.pulse_off()
        self.MOTTimer.stop()

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

    def GoAction(self):
        self.loadData()
        self.MOTTimer.stop()
        self.pulse_off()
        self.doGo()
        self.updateDC()
        if self.cbMOTLoad.isChecked():
          self.MOTTimer.start(100)
          self.pulse_on()

    def loadData(self):
        stages=self.Stages.stages
        devIDs = self.Stages.devIDs
        self.totaltime=0.0
        self.timestep=0.05/(1.0+0.0625e-3)
        self.totaltime=sum([stage.time.value() for stage in stages])
        nsteps=int(self.totaltime/self.timestep+1) # assuming timesteps of 0.1 ms

        data=np.zeros((nsteps,lengths(self.devicenames['DAC']),dtype=int)
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
            if length(self.devicenames['AOM'])>0:
              for AOM in range(length(self.devicenames['AOM'])/2): # Prepare message for 1st AOM
                t1=devIDs['AOM'][2*AOM]
                if tid==0: # We need a special case for the first column, we need to compare to DC value rather than previous column
                    t2=AOM+10
                    temp=stages[tid].boxes[t1].value()
                    if temp!=self.Stages.DC[t1].value():
                        msg=msg+str(t2)+','+'FREQ,'+str(AOM)+','+str(temp)+','
                        
                    temp=stages[tid].boxes[t1+1].value()
                    if temp!=self.Stages.DC[t1+1].value():
                        msg=msg+str(t2)+','+'AMPL,'+str(AOM)+','+str(temp)+','
                else:
                    temp=stages[tid].boxes[t1].value()
                    if temp!=stages[tid-1].boxes[t1].value():
                        msg=msg+str((int(thetime*1000)+AOM))+','+'FREQ,'+str(AOM)+','+str(temp)+','
                    temp=stages[tid].boxes[t1+1].value()
                    if temp!=stages[tid-1].boxes[t1+1].value():
                        msg=msg+str((int(thetime*1000)+AOM))+','+'AMPL,'+str(AOM)+','+str(temp)+','
              for DIOid in devIDs['DIO']
                if col==0:
                    t1=self.DCDIOboxes[DIOid].isChecked()
                else:
                    t1=stages[tid-1].boxes[DIOid].isChecked()
                t2=stages[tid].boxes[DIOid].isChecked()
                if (t1 != t2):
                    msg=msg+str(int(thetime*1000)+14+trig)+",TRIG,"+str(trig)+','+str(int(t2))+','
                    
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
        if self.nAOMs>4:
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
              self.parent().bfcam.show(nshots)
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



    def valuechange(self,i,j):
       print(self.Spinboxes[self.i][self.j].value())


if __name__=='__main__':
  npts=100000
  da.GetDevices()
  import time
  #t=np.arange(npts)/npts
  #data=np.zeros((npts,8))
  #for j in range(8):
    #data[:,j]=np.sin(10*t+j)**2*4096
  #data2=data.flatten('C').astype(np.ushort)
  #print(data2[0:10])
  #print(data2.shape)
  #data2[-1]+=0x8000
  ##result=da.DACOutputProcess(0,20000,8*npts,data2)
  #freq=20000
  #datalen=8*npts
  #result=da.DACOutputProcess(0,freq,datalen,data2)
  #print(result)
  while (1):
    da.DACDirect(0,3,4095)
    time.sleep(1)
    da.DACDirect(0,3,0)
    time.sleep(1)
