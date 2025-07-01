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
    def __init__(self,ndacs,naoms,ntimes):
      super(allboxes, self).__init__()
      try:
          print(da.GetDevices()) # This is required for all apps using the DAC
      except:
          print("DA not present")
          self.DApresent=False
      #self.setWidgetResizable(True)
      #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
      self.ntimes=ntimes
      self.nDACs=ndacs
      self.nAOMs=naoms
      self.nDIOs=2
      #self.setFixedHeight(700)
      #self.setFixedWidth(900)
      self.nrows=self.nDACs+2*self.nAOMs
      self.layout = QGridLayout(self)
      self.layout.setSpacing(1)
      self.aomlist = [AOM+suffix for AOM in aom_names for suffix in [' ']]
      self.devicenames={'DAC':dac_names, 'AOM':aom_names,'EagleDAC':EDnames}
      self.DAClabels=[]
      self.AOMlabels=[]
      self.Spinboxes=[]
      self.DIOboxes=[]
      self.DIOlabels=[]
      self.Timeboxes=[]
      self.DCSpinboxes=[]
      self.DCDIOboxes=[]
      self.stagelabels=[]
      
      self.hlines=1
      self.stagenames=['Stage '+str(i+1) for i in range(8)]
      for n in range(len(self.stagenames)):
          self.stagelabels.append(QLabel(self.stagenames[n]))
          self.layout.addWidget(self.stagelabels[-1],0,n+2)
      self.RF_currentstage = 0 # Need to load this from FITS file if/when appropriate
      #self.testbox=QMSbox(345,544)
      self.testbox=QLabel('DC Values')
      #self.testbox.setFont(QFont('Arial',7))
      
      self.layout.addWidget(self.testbox,self.hlines,0)
      #self.testbox.valueChanged.connect(self.testbox.valuechange)
      #self.testbox.
      self.Timelabel=QLabel('Time (ms)')
      #self.Timelabel.setFont(QFont('Arial',7))
      self.layout.addWidget(self.Timelabel,self.hlines,1)
      for i in range(self.ntimes):
          self.Timeboxes.append(Timebox())
          #self.Timeboxes[-1].setFont(QFont('Arial',7))
          self.layout.addWidget(self.Timeboxes[i],self.hlines,i+2)
          self.Timeboxes[i].valueChanged.connect(self.change_RF_stage)
      for i in range(self.nDACs):
          self.DCSpinboxes.append(DC_DAC_Box(self.hlines,i))
          #self.DCSpinboxes[-1].setFont(QFont('Arial', 7))
          self.layout.addWidget(self.DCSpinboxes[i],self.hlines+i+1,0)
      for i in range(self.nDIOs):
          self.DCDIOboxes.append(DC_DIO_Box(i))
          self.layout.addWidget(self.DCDIOboxes[i],self.hlines+i+1+self.nDACs,0)
      for i in range(2*self.nAOMs):
          j=i//2
          if ((i%2) == 0) :
              self.DCSpinboxes.append(DC_AOM_Freq_Box(self.hlines,j))
          else:
              self.DCSpinboxes.append(DC_AOM_Ampl_Box(self.hlines,j))
          #self.DCSpinboxes[-1].setFont(QFont('Arial', 7))
          self.layout.addWidget(self.DCSpinboxes[i+self.nDACs],self.hlines+i+self.nDACs+1+self.nDIOs,0)
          #self.DCSpinboxes[i].valueChanged.connect(self.DCSpinboxes[i].valuechange)
      for i in range(self.nDACs):
          self.DAClabels.append(QLabel(dac_names[i]))
          #self.DAClabels[-1].setFont(QFont('Arial', 7))
          self.layout.addWidget(self.DAClabels[i],self.hlines+i+1,1)
      for i in range(2*self.nAOMs):
          aomno=i//2
          if (i%2==0):
              mystr=" Freq "
          else:
              mystr=" Ampl "
          self.AOMlabels.append(QLabel(aom_names[aomno]+mystr))
          #self.AOMlabels[-1].setFont(QFont('Arial',8))
          #self..setAlignment(Qt.AlignCenter)
          self.layout.addWidget(self.AOMlabels[i],self.hlines+i+self.nDACs+self.nDIOs+1,1)
      DIOnames=['RF Ramp Trigger','Unused']
      for i in range(len(DIOnames)):
        self.DIOlabels.append(QLabel(DIOnames[i]))
        self.layout.addWidget(self.DIOlabels[i],self.hlines+i+self.nDACs+1,1)
      for j in range(self.ntimes):
          self.Spinboxes.append([])
          self.DIOboxes.append([])
          for i in range(self.nDACs):
              #print(i,j)
              self.Spinboxes[j].append(DAC_Box(i,j))
              self.layout.addWidget(self.Spinboxes[j][i],self.hlines+i+1,j+2)
              #self.Spinboxes[j][i].setRange(-10,10)
          for i in range(self.nDIOs):
              self.DIOboxes[j].append(QCheckBox())
              print(i,j)
              self.layout.addWidget(self.DIOboxes[j][i],self.hlines+i+self.nDACs+1,j+2)
          for i in range(2*self.nAOMs):
              if (i%2==0):
                  self.Spinboxes[j].append(AOM_Freq_Box(i+self.nDACs,j))
                  #self.Spinboxes[j][-1].setValue(80.0)
              else:
                  self.Spinboxes[j].append(AOM_Ampl_Box(self.hlines+i+self.nDACs,j))
                  #self.Spinboxes[j][-1].setValue(1.0)
              self.layout.addWidget(self.Spinboxes[j][i+self.nDACs],self.hlines+i+self.nDACs+self.nDIOs+1,j+2)
              #self.Spinboxes[j][i].valueChanged.connect(self.valuechange(i,j))
      self.eagledac=eagle.EaglePanel()
      self.layout.addWidget(self.eagledac,self.hlines+40,0,4,5)
      ##self.cambox=QSpinBox()
      #self.layout.addWidget(self.cambox,44,4)
      #self.camlabel=QLabel('Camera shots')
      #self.layout.addWidget(self.camlabel,44,3)
      self.GoButton=QPushButton('Go')
      self.CycleButton=QPushButton('Cycle')
      self.layout.addWidget(self.GoButton,self.hlines+44,1)
      self.layout.addWidget(self.CycleButton,self.hlines+45,1)

      self.cbPictype=QComboBox()
      self.cbPictype.addItem("No picture")
      self.cbPictype.addItem("One shot")
      self.cbPictype.addItem("Fluorescence")
      self.cbPictype.addItem("Shadow image")
      self.layout.addWidget(self.cbPictype,self.hlines+44,2)
      self.setLayout(self.layout)
      self.setWindowTitle("Simple Experiment Controller")
      self.GoButton.clicked.connect(self.GoAction)
      self.CycleButton.clicked.connect(self.CycleAction)
      self.camera=camera_test.camera()
      #self.EDRE=DAQ.EDRE_Interface()
      self.cycling=False
      self.cbMOTLoad=QCheckBox()
      self.cbMOTLoad.stateChanged.connect(self.TimerChange)
      self.MOTLoadLabel=QLabel('Load MOT')
      self.layout.addWidget(self.cbMOTLoad,self.hlines+44,0)
      self.layout.addWidget(self.MOTLoadLabel,self.hlines+45,0)
      self.MOTTimer=QTimer(self)
      self.MOTTimer.timeout.connect(self.MOTTimerAction)
      self.MGPanel=mg.MultiGoPanel()
      self.layout.addWidget(self.MGPanel,self.hlines+40,7,5,2)
      self.MultiGoButton=QPushButton('MultiGo')
      self.layout.addWidget(self.MultiGoButton,self.hlines+45,7)
      self.MultiGoButton.clicked.connect(self.MultiGo)
      self.MGParamButton=QPushButton('Parameters')
      self.layout.addWidget(self.MGParamButton,self.hlines+45,8)
      self.MGParamButton.clicked.connect(self.mgmenu)
      # self.cbExpKind=QComboBox()
      # self.cbExpKind.addItem('X Field')
      # self.cbExpKind.addItem('Y Field')
      # self.cbExpKind.addItem('Z Field')
      # self.sbExpFrom=QDoubleSpinBox()
      # self.sbExpFrom.setValue(0.0)
      # self.sbExpTo=QDoubleSpinBox()
      # self.sbExpTo.setValue(1.0)
      # self.layout.addWidget(self.sbExpFrom,40,6)
      # self.layout.addWidget(self.sbExpTo,41,6)
      # self.layout.addWidget(self.cbExpKind,42,6)
      # self.mgCount=QLabel('0 of '+str(self.sbNCycles.value()))
      # self.layout.addWidget(self.mgCount,45,6)
      self.fluo=QLCDNumber()
      self.layout.addWidget(self.fluo,self.hlines+45,2)
      # self.RF_stop_freq=QDoubleSpinBox()
      # self.RF_stop_freq.setValue(1.0)
      # self.RF_stop_label=QLabel("RF stop")
      # self.layout.addWidget(self.RF_stop_freq,45,4)
      # self.layout.addWidget(self.RF_stop_label,45,3)
      # self.RF_stop_freq.valueChanged.connect(self.Change_RF_stopF)
      # self.RF_start_freq=QDoubleSpinBox()
      # self.RF_start_freq.setValue(4.5)
      # self.RF_start_label=QLabel("RF start")
      # self.layout.addWidget(self.RF_start_freq,44,4)
      # self.layout.addWidget(self.RF_start_label,44,3)
      # self.RF_start_freq.valueChanged.connect(self.Change_RF_startF)
      # self.RF_time_label=QLabel("RF time (ms)")
      # self.layout.addWidget(self.RF_time_label,44,6)
      # self.RF_sweep_time=QDoubleSpinBox()
      # self.layout.addWidget(self.RF_sweep_time,44,7)
      # self.RF_sweep_time.valueChanged.connect(self.Change_RF_length)
      # self.RF_sweep_time.setRange(0,100000)
      # self.RF_sweep_time.setValue(1000)
      # self.RF_amplitude=QDoubleSpinBox()
      # self.RF_ampl_label=QLabel("RF Amplitude (mV)")
      # self.RF_amplitude.valueChanged.connect(self.Change_RF_amplitude)
      # self.RF_amplitude.setRange(0,1000)
      # self.RF_amplitude.setValue(150)
      # self.layout.addWidget(self.RF_ampl_label,45,6)
      # self.layout.addWidget(self.RF_amplitude,45,7)
      self.tek=afg.TekAFG()
      #try:
          
      self.tek.RF_stop_freq.setValue(1.0)
      self.tek.RF_start_freq.setValue(4.5)
      #self.tek.RF_sweep_time.setValue(1000)
      self.tek.RF_amplitude.setValue(150)
          
      self.loadRFStages()
      self.tek.RF_stage_select.currentIndexChanged.connect(self.change_RF_stage)
          
          #self.tek.setLayout(self.tek.layout)
          
          #self.cbPictype=QComboBox()
          #self.cbPictype.addItem("No picture")
          #self.cbPictype.addItem("One shot")
          #self.cbPictype.addItem("Fluorescence")
          #self.cbPictype.addItem("Shadow image")
      #except:
      #    pass
      self.layout.addWidget(self.tek,self.hlines+40,5,5,2)
      try:
          self.adc=adclib.adc()
      except:
          pass

    def mgmenu(self):
        mg.multigomenu(self.MGPanel,self.devicenames,self.stagenames)
        self.fill_MG_files()
        
    def loadRFStages(self):
        self.tek.RF_stage_select.clear()
        self.tek.RF_stage_select.addItems(self.stagenames)

    def which_RF_stage(self):
        name=self.tek.RF_stage_select.currentText()
        index = [i for i in range(len(self.stagenames)) if self.stagenames[i] == name]
        assert len(index)==1; 'You have multiple stages sharing the same label - please give them all unique labels!'
        return index[0]

    def change_RF_stage(self):
        ind = self.which_RF_stage()
        newvalue=self.Timeboxes[ind].value()
        self.tek.Change_RF_stage(newvalue)
        self.RF_currentstage = ind
        
    def fill_MG_files(self):
        self.MGPanel.cbExpKind.clear()
        flist=sorted(glob.glob("*.mgo"))
        for item in flist:
          sitem=item[:-4]
          self.MGPanel.cbExpKind.addItem(sitem)

    def MOTTimerAction(self):
#        if self.nAOMs>0:
#          self.DCSpinboxes[9+2].setValue(0.0)
#          self.DCSpinboxes[9+6].setValue(0.4)
#          time.sleep(0.02)
#          self.DCSpinboxes[9+2].setValue(1.0)
#          self.DCSpinboxes[9+6].setValue(0.0)
          self.fluo.display(self.adc.read(0))
          #print("cycle")
#        else:
#          self.DCSpinboxes[18].setValue(0.0)
#          self.DCSpinboxes[20].setValue(5.0)
#          time.sleep(0.02)
#          self.DCSpinboxes[18].setValue(5.0)
#          self.DCSpinboxes[20].setValue(0.0)
    def pulse_on(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml='PULSE,ON'
        #print(ml)
        s.send(ml.encode())
        s.recv(5)
        s.close()

    def pulse_off(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml='PULSE,OFF'
        #print(ml)
        s.send(ml.encode())
        s.recv(5)
        s.close()

   #def read_mg_pars(self,filename):
   #     if os.path.exists(filename):
   #         f=open(filename,"r")
   #         ls=f.readlines()
   #         params=[]
   #         for l in ls:
   #           p=l.split(' ')
   #           params.append(p)
   #         f.close()
   #         return(params)
   #     else:
   #         return(-999)
    #class Parameter():
    #    def __init__(self):
    #      self.b_val=0.0
    #      self.e_val=1.0
    #      self.time=1
    #      self.channel=0
    #      self.title='Test'

    #def read_mg_pars(self,filename):
    #    if os.path.exists(filename):
    #        f=open(filename,"r")
    #        ls=f.readlines()
    #        print("Reading ",filename)
    #        params=[]
    #        for l in ls:
    #          par=self.Parameter()
    #          p=l.split(' ')
    #          print(l,p)
    #          par.b_val=float(p[1])
    #          par.title=p[0]
    #          par.e_val=float(p[2])
    #          par.time=int(p[3])
    #          par.channel=int(p[4])
    #          params.append(par)
    #        f.close()
    #        return(params)
    #    else:
    #        return(-999)


    def MultiGo(self):
       self.MOTTimer.stop()
       self.pulse_off()
       eid=self.MGPanel.cbExpKind.currentIndex()
       npts=self.MGPanel.sbNCycles.value()
       if eid<3:
         b_val=self.MGPanel.sbExpFrom.value()
         e_val=self.MGPanel.sbExpTo.value()
         dacid=self.MGPanel.cbExpKind.currentIndex()+3
         #npts=self.sbNCycles.value()
       else:
         fname=self.MGPanel.cbExpKind.currentText()+'.mgo'
         mgpars = mg.Parameters(self.devicenames,self.stagenames)
         mgpars.newread(fname)
         #mgpars=self.read_mg_pars(fname)
         #for par in mgpars:
         # bval
         #b_val=mgpars[1]
         #e_val=mgpars[2]
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
                     self.Timeboxes[tid].setValue(myvalue)
                 elif mytype=='RF (freq)' or mytype=='RF (amp)':
                     #self.tek.Change_RF_length(self.Timeboxes[tid].value()) # Not necessary, I think; should be changed automatically when RF stage select adjusts stage ID.
                     self.Spinboxes[tid][4].setValue(0.0)
                     for i in range(len(self.stagenames)):
                         self.DIOboxes[i][0].setChecked(False)
                     self.DIOboxes[tid][0].setChecked(True)
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
                 elif mytype=='AOM':
                     self.Spinboxes[tid][cid+8].setValue(myvalue)
                 else:
                     self.Spinboxes[tid][cid].setValue(myvalue)
         self.pulse_off()
         QApplication.processEvents()
         self.loadData()
         self.doGo()
         filename=datapath+'/'+mydate+'/Data_'+str(i)+'.fit'
         self.parent().mysave(filename)
         for i in range(self.nDACs):
           self.DCSpinboxes[i].updateDAC()
           #print(i)
         for i in range(self.nDACs,self.nDACs+2*self.nAOMs):
           self.DCSpinboxes[i].update()
         self.pulse_on()
         time.sleep(10)

           #QApplication.processEvents()



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


    def DelCol(self,where):
        print(where)
        where=where-1
        ntimes=self.ntimes
        import sip
        for i in range(ntimes-where-1):
            print(i+where)
            self.Timeboxes[i+where].setValue(self.Timeboxes[i+where+1].value())
        self.layout.removeWidget(self.Timeboxes[-1])
        sip.delete(self.Timeboxes[-1])
        for col in range(ntimes-where-1):
            for row in range(self.nrows):
                self.Spinboxes[col+where][row].setValue(self.Spinboxes[col+where+1][row].value())
        for row in range(self.nrows):
            self.layout.removeWidget(self.Spinboxes[-1][row])
            sip.delete(self.Spinboxes[-1][row])
        self.ntimes=ntimes-1
        self.Spinboxes.pop()

    def DupCol(self,where):
        print(where)
        ntimes=self.ntimes
        #where=self.where
        #self.ntimes+=1
        #self.Timeboxes.insert(where,QDoubleSpinBox())
        #self.Timeboxes[where+1].setValue(self.Timeboxes[where].value())
        self.AddCol()
        steps=ntimes-where
        for i in range(steps):
            self.Timeboxes[ntimes-i].setValue(self.Timeboxes[ntimes-i-1].value())
            for j in range(self.nrows):
                self.Spinboxes[ntimes-i][j].setValue(self.Spinboxes[ntimes-i-1][j].value())

    def AddCol(self):
        self.ntimes+=1
        self.parent().coldup_actions.append(QAction('Column '+str(self.ntimes),self))
        self.parent().column_dup.addAction(self.parent().coldup_actions[-1])
        self.stagelabels.append(QLabel('Stage '+str(self.ntimes)))
        self.layout.addWidget(self.stagelabels[-1],0,self.ntimes+1)
        self.Timeboxes.append(Timebox())
        #self.Timeboxes[-1].setFont(QFont('Arial', 7))
        self.layout.addWidget(self.Timeboxes[-1],self.hlines,self.ntimes+1)
        self.Spinboxes.append([])
        self.DIOboxes.append([])
        for i in range(self.nDACs):
            self.Spinboxes[-1].append(DAC_Box(i,self.ntimes-1))
            self.layout.addWidget(self.Spinboxes[-1][-1],i+2,self.ntimes+1)
        for i in range(2*self.nAOMs):
            self.Spinboxes[-1].append(QMSbox(i+self.nDACs,self.ntimes-1))
            if (i%2==0):
                self.Spinboxes[-1][-1].setValue(80.0)
            else:
                self.Spinboxes[-1][-1].setValue(1.0)
            self.layout.addWidget(self.Spinboxes[-1][-1],i+4+self.nDACs,self.ntimes+1)
        for i in range(self.nDIOs):
             self.DIOboxes[-1].append(QCheckBox())
             self.layout.addWidget(self.DIOboxes[-1][i],self.hlines+i+self.nDACs+1,self.ntimes+1)

    def GoAction(self):
        self.loadData()
        self.MOTTimer.stop()
        self.pulse_off()
        #self.DCSpinboxes[20].setValue(5.0)
        #self.DCSpinboxes[18].setValue(5.0)
        self.doGo()
        for i in range(self.nDACs):
          self.DCSpinboxes[i].updateDAC()
          #print(i)
        for i in range(self.nDACs,self.nDACs+2*self.nAOMs):
          self.DCSpinboxes[i].update()
          #print(i)
        if self.cbMOTLoad.isChecked():
          self.MOTTimer.start(100)
          self.pulse_on()


    def loadData(self):
        self.totaltime=0.0
        self.timestep=0.05/(1.0+0.0625e-3)
        #self.timestep=0.05*(1.0-0.06e-3)
        for col in range(self.ntimes):
            self.totaltime+=self.Timeboxes[col].value()
        nsteps=int(self.totaltime/self.timestep+1) # assuming timesteps of 0.1 ms
        #if nsteps < 65536:
        #  size = 65560
        #else:
        #  size = nsteps
        data=np.zeros((nsteps,self.nDACs),dtype=int)
        timestepstilnow=0
        thetime=0.0
        msg='LOAD,'
        msg2='LOAD,'
        for col in range(self.ntimes):
            timesteps=int(self.Timeboxes[col].value()/self.timestep)
            for t in range(timesteps):
                i = t + timestepstilnow
                for row in range(self.nDACs):
                    temp=self.Spinboxes[col][row].value()
                    if ((temp>=0.0) and (temp<=5.0)):
                        data[i,row]=int(temp*MAX_INT/5.0)
                    elif (temp==-20.0):
                        tmp2=self.Spinboxes[col][row].LOffset+self.Spinboxes[col][row].LAmp/(1.0+(t*self.timestep/self.Spinboxes[col][row].LTc)**2)
                        data[i,row]=int(tmp2*MAX_INT/5.0)
                    elif (temp==-30.0):
                        tmp2=self.Spinboxes[col][row].RStart+t*(self.Spinboxes[col][row].REnd-self.Spinboxes[col][row].RStart)/timesteps
                        data[i,row]=int(tmp2*MAX_INT/5.0)
            timestepstilnow+=timesteps
            self.data=data
            if self.nAOMs>0:
              for AOM in range(4): # Prepare message for 1st AOM
                t1=2*AOM+self.nDACs
                if col==0: # We need a special case for the first column, we need to compare to DC value rather than previous column
                    temp=self.Spinboxes[col][t1].value()
                    t2=AOM+10
                    if temp!=self.DCSpinboxes[t1].value():
                        msg=msg+str(t2)+','+'FREQ,'+str(AOM)+','+str(temp)+','
                    temp=self.Spinboxes[col][t1+1].value()
                    if temp!=self.DCSpinboxes[t1+1].value():
                        msg=msg+str(t2)+','+'AMPL,'+str(AOM)+','+str(temp)+','
                else:
                    temp=self.Spinboxes[col][t1].value()
                    if temp!=self.Spinboxes[col-1][t1].value():
                        msg=msg+str((int(thetime*1000)+AOM))+','+'FREQ,'+str(AOM)+','+str(temp)+','
                    temp=self.Spinboxes[col][t1+1].value()
                    if temp!=self.Spinboxes[col-1][t1+1].value():
                        msg=msg+str((int(thetime*1000)+AOM))+','+'AMPL,'+str(AOM)+','+str(temp)+','
              for trig in range(self.nDIOs):
                if col==0:
                    t1=self.DCDIOboxes[trig].isChecked()
                else:
                    t1=self.DIOboxes[col-1][trig].isChecked()
                t2=self.DIOboxes[col][trig].isChecked()
                if (t1 != t2):
                    msg=msg+str(int(thetime*1000)+14+trig)+",TRIG,"+str(trig)+','+str(int(t2))+','
            if self.nAOMs>4:
              n2=self.nAOMs-4
              for AOM in range(n2): # Same for second AOM
                t1=2*AOM+self.nDACs+8
                if col==0:
                    temp=self.Spinboxes[col][t1].value()
                    print(temp,t1,self.DCSpinboxes[t1].value())
                    if temp!=self.DCSpinboxes[t1].value():
                        msg2=msg2+'10,'+'FREQ,'+str(AOM)+','+str(temp)+','
                    temp=self.Spinboxes[col][t1+1].value()
                    if temp!=self.DCSpinboxes[t1+1].value():
                        msg2=msg2+'10,'+'AMPL,'+str(AOM)+','+str(temp)+','
                else:
                    temp=self.Spinboxes[col][t1].value()
                    if temp!=self.Spinboxes[col-1][t1].value():
                        msg2=msg2+str((int(thetime*1000)))+','+'FREQ,'+str(AOM)+','+str(temp)+','
                    temp=self.Spinboxes[col][t1+1].value()
                    if temp!=self.Spinboxes[col-1][t1+1].value():
                        msg2=msg2+str((int(thetime*1000)))+','+'AMPL,'+str(AOM)+','+str(temp)+','
            thetime=thetime+self.Timeboxes[col].value()
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
        #self.nsamples=size
        self.nsamples=timestepstilnow
        #print(data.shape,nsamples)
        #print(nsamples)

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
        #print("Data shape is ",data.shape)
        #print("First 10 points ",data[0:10])
        freq=20000
        #print(data[24:34])
        #self.EDRE.stop(0)
        #self.EDRE.run(0,self.nsamples,data)
        #time.sleep(self.nsamples*50e-6+0.001)
        #self.EDRE.stop(0)
        result=da.DACOutputProcess(0,freq,datalen,data)
        time.sleep(1)
        #print("Result is ",result,nsamples)
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
        #plt.plot(self.data[:,0])
        #plt.show()


    def valuechange(self,i,j):
       print(self.Spinboxes[self.i][self.j].value())
      #self.l1.setText("current value:"+str(self.sp.value()))

    # def Change_RF_stopF(self):
    #   newvalue=self.RF_stop_freq.value()*1e6
    #   import pyvisa
    #   rm=pyvisa.ResourceManager('@py')
    #   #rm.open_resource('TCPIP::130.216.50.90::INSTR')
    #   afg=rm.open_resource('TCPIP::130.216.50.90::INSTR')
    #   afg.write('SOUR1:FREQ:STOP '+str(newvalue))
    #   afg.close()
    #
    # def Change_RF_startF(self):
    #   newvalue=self.RF_start_freq.value()*1e6
    #   import pyvisa
    #   rm=pyvisa.ResourceManager('@py')
    #   #rm.open_resource('TCPIP::130.216.50.91::INSTR')
    #   afg=rm.open_resource('TCPIP::130.216.50.90::INSTR')
    #   afg.write('SOUR1:FREQ:START '+str(newvalue))
    #   afg.close()
    #
    # def Change_RF_length(self):
    #   newvalue=self.RF_sweep_time.value()
    #   import pyvisa
    #   rm=pyvisa.ResourceManager('@py')QCheckBox()
    #   #rm.open_resource('TCPIP::130.216.50.91::INSTR')
    #   afg=rm.open_resource('TCPIP::130.216.50.90::INSTR')
    #   afg.write('SOUR1:SWE:TIME '+str(newvalue)+'ms')
    #   afg.close()
    #
    # def Change_RF_amplitude(self):
    #   newvalue=self.RF_amplitude.value()/1000
    #   import pyvisa
    #   rm=pyvisa.ResourceManager('@py')
    #   #rm.open_resource('TCPIP::130.216.50.91::INSTR')
    #   afg=rm.open_resource('TCPIP::130.216.50.90::INSTR')
    #   afg.write('SOUR1:VOLT:LEV:IMM:AMPL '+str(newvalue)+'Vpp')
    #   afg.close()



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
