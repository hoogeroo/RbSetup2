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

#class allboxes(QFrame,fitsfile):



class spindemo(QFrame):
    def __init__(self):
      super(spindemo, self).__init__()
      self.ntimes=10
      self.nDACs=24
      self.nAOMs=4
      self.nrows=self.nDACs+2*self.nAOMs
      layout = QGridLayout(self)
      layout.setSpacing(2)
      self.DAClabels=[]
      self.AOMlabels=[]
      self.Spinboxes=[]
      #self.DIOboxes=[]
      self.Timeboxes=[]
      self.DCSpinboxes=[]
      #self.DCDIOboxes=[]
      self.testbox=QMSbox(345,544)
      layout.addWidget(self.testbox,0,0)
      self.testbox.valueChanged.connect(self.testbox.valuechange)
      #self.testbox.
      for i in range(self.ntimes):
          self.Timeboxes.append(QDoubleSpinBox())
          layout.addWidget(self.Timeboxes[i],0,i+2)
      for i in range(self.nDACs):
          self.DCSpinboxes.append(QDoubleSpinBox())
          layout.addWidget(self.DCSpinboxes[i],i+1,0)
      for i in range(2*self.nAOMs):
          self.DCSpinboxes.append(QDoubleSpinBox())
          layout.addWidget(self.DCSpinboxes[i+self.nDACs],i+self.nDACs+1,0)
          #self.DCSpinboxes[i].valueChanged.connect(self.DCSpinboxes[i].valuechange)
      for i in range(self.nDACs):
          self.DAClabels.append(QLabel('DAC # '+str(i)))
          layout.addWidget(self.DAClabels[i],i+1,1)
      for i in range(2*self.nAOMs):
          aomno=i//2
          if (i%2==0):
              mystr=" Freq "
          else:
              mystr=" Ampl "
          self.AOMlabels.append(QLabel('AOM # '+str(aomno)+mystr))
          #self..setAlignment(Qt.AlignCenter)
          layout.addWidget(self.AOMlabels[i],i+25,1)
      for j in range(self.ntimes):
          self.Spinboxes.append([])
          #self.DIOboxes.append([])
          for i in range(self.nDACs):
              #print(i,j)
              self.Spinboxes[j].append(QMSbox(i,j))
              layout.addWidget(self.Spinboxes[j][i],i+1,j+2)
              self.Spinboxes[j][i].setRange(-10,10)
          for i in range(2*self.nAOMs):
              self.Spinboxes[j].append(QMSbox(i+self.nDACs,j))
              layout.addWidget(self.Spinboxes[j][i+24],i+24+1,j+2)
              #self.Spinboxes[j][i].valueChanged.connect(self.valuechange(i,j))
      self.GoButton=QPushButton('Go')
      self.CycleButton=QPushButton('Cycle')
      layout.addWidget(self.GoButton,34,1)
      layout.addWidget(self.CycleButton,34,2)
      self.setLayout(layout)
      self.setWindowTitle("Simple Experiment Controller")
      self.GoButton.clicked.connect(self.GoAction)

    def GoAction(self):
        totaltime=0.0
        self.timestep=0.1
        for col in range(self.ntimes):
            totaltime+=self.Timeboxes[col].value()
        nsteps=int(totaltime/self.timestep) # assuming timesteps of 0.1 ms
        data=np.zeros((nsteps,self.nrows),dtype=int)
        timestepstilnow=0
        for col in range(self.ntimes):
            timesteps=int(self.Timeboxes[col].value()/self.timestep)
            for t in range(timesteps):
                i = t + timestepstilnow
                for row in range(self.nrows):
                    temp=self.Spinboxes[col][row].value()
                    if ((temp>=-10.0) and (temp<=10.0)):
                        data[i,row]=int(temp*1e6)
                    elif (temp==-20.0):
                        tmp2=self.Spinboxes[col][row].LOffset+self.Spinboxes[col][row].LAmp/(1.0+(t*self.timestep/self.Spinboxes[col][row].LTc)**2)
                        data[i,row]=int(tmp2*1e6)
                    elif (temp==-30.0):
                        tmp2=self.Spinboxes[col][row].RStart+t*(self.Spinboxes[col][row].REnd-self.Spinboxes[col][row].RStart)/timesteps
                        data[i,row]=int(tmp2*1e6)
            timestepstilnow+=timesteps
        plt.plot(data[:,1])
        plt.show()


    def valuechange(self,i,j):
       print(self.Spinboxes[self.i][self.j].value())
      #self.l1.setText("current value:"+str(self.sp.value()))
