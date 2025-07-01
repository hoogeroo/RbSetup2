import numpy as np
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import astropy.io.fits as fits

from qmsbox import *
from dacprops import *
import tek_afg as afg
try:
    import EagleDAC_main as eagle
    import adclib
except:
    pass
import astropy.io.fits as fits

class newStage():
  def __init__(self,name,stageid, t,devdict):
    self.name=name
    self.sID = stageid
    self.time=Timebox()
    self.time.setValue(t)
    self.boxes=[]
    for devtype, devices in devdict:
      if devtype=='DAC':
        for i in range(len(devices)):
          self.boxes.append(DAC_Box(1,i))
      elif devtype=='DIO':
        for i in range(len(devices)):
          self.boxes.append(QCheckBox())
      elif devtype=='AOM':
        for i in range(len(devices)):
            if (i%2==0):
                self.boxes.append(AOM_Freq_Box(i+len(devdict['DAC']),stageid))
            else:
                self.boxes.append(AOM_Ampl_Box(1+i+len(devdict['DAC']),stageid))
      elif devtype != 'EagleDAC':
        Exception('Too many different device types!')
        
    #self.order=[]

class Stages():
  def __init__(self,devdict=[], table=[], curves=[], DIOstate=[], nstages=8):
    self.devices=devdict
    self.devIDs=Dict()
    total=0
    for key in self.devices.keys:
        self.devIDs[key]=list(range(total,total+self.devices[key]))
        total+=self.devices[key]
    
    
    self.stages=[]
    
    self.DC=[]
    self.addDC()
            
    if table:
      self.populate(table,curves,DIOstate)
    else:
      for i in range(nstages):
        self.addStage()
    
  def addStage(self,time=0,vals=[],DIOstate=[],position='last'):
    stageid = len(self.stages)
    self.stages.append(newStage('Stage '+str(stageid),stageid, time, self.devices))
    
    valcount=0
    iocount=0
    stagevals=self.stages[-1].boxes
    for i in range(len(stagevals)):
      if isinstance(stagevals[i], QCheckBox) and DIOstate:
        stagevals[i].isChecked(DIOstate[iocount])
        iocount+=1
      else if vals:
        stagevals[i].setValue(vals[valcount])
        valcount+=1
                     
    if position=='last' or position > stageid-1:
      continue
    else:
      self.stages = [self.stages[:position],self.stages[-1], self.stages[position:-1]
  
  def addDC(self):
    for devtype, devices in self.devices:
      if devtype=='DAC':
        for i in range(len(devices)):
          self.DC.append(DC_DAC_Box(1,i))
      elif devtype=='DIO':
        for i in range(len(devices)):
          self.DC.append(DC_DIO_Box(i))
      elif devtype=='AOM':
        for i in range(len(devices)):
            j=i//2
            if (i%2==0):
                self.DC.append(DC_AOM_Freq_Box(1,j))
            else:
                self.DC.append(DC_AOM_Ampl_Box(1,j))
      elif devtype != 'EagleDAC':
        Exception('Too many different device types!')
  
  def delStage(self,position='last'):
    if position = 'last' or position > len(self.stages):
      del self.stages[-1]
    else:
      del self.stages[position]
    
  def dupStage(self,a,position='last'):
    stagecopy=self.stage[a]
    values = [x.value() for x in stagecopy.vals if not isinstance(x,QCheckBox)]
    DIOstate = [x.isChecked() for x in stagecopy.vals if isinstance(x,QCheckBox)]
    
    self.addStage(stagecopy.time, values,DIOstate, position)
    
  def swapStage(self,a,b):
    self.stages[a], self.stages[b] = self.stages[b], self.stages[a]
  
  def updateorder(self,neworder):
    self.stages=self.stages[neworder]
    
  def populate(self, table,curves,DIOstate):
    for i in self.stages:
      self.delStage()
      
    dc_vals = table[1:,0]
    
    valcount=0
    iocount=0
    for i in range(len(self.DC)):
      if isinstance(self.DC[i],QCheckBox):
        self.DC[i].setChecked(DIOstate[iocount,0])
        iocount+=1
      else:
        self.DC[i].setValue(dc_vals[valcount])
        valcount+=1
    for j in range(len(times)):
      self.addStage(time=table[0,j+1],vals=table[1:,j+1],DIOstate=DIOstate[j+1])
    
  def store(self):
    columns=[]
    curves=[]
    DIOstate=[]
    
    DC_vals = [x.value() for x in self.DC if not isinstance(x, QCheckBox)]
    DC_vals.insert(0,0.0)
    columns.append(fits.Column('DC'+str(len(DC_vals)), array=np.array(DC_vals), format='E'))
    
    DC_DIOval=[x.isChecked() for x in self.DC if isinstance(x,QCheckBox)]
    DIOstate.append(fits.Column('DCDIO '+str(i), array=np.array(DC_DIOval), format='E'))
    
    for i in range(len(self.stages)):
      DIOval=[]
      col=[box.value() for box in self.stages[i].boxes if not isinstance(box, QCheckBox)]
      col.insert(0,self.stages[i].time.value())
      columns.append(fits.Column('Time '+str(i), array=np.array(col), format='E'))
      
      DIOval=[box.isChecked() for box in self.stages[i].boxes if isinstance(box,QCheckBox)]
      DIOstate.append(fits.Column('TimeDIO '+str(i), array=np.array(DIOval), format='E'))
      
      indices = np.where(col < -15)
      for index in indices:
        box=self.stages[i].boxes[index]
        
        if col[index]==-20.:
          curves.append(fits.Column("Lorentz"+str(i)+str(index), np.array([-20., box.Loffset, box.LAmp, box.LTc]), format='E'))
        elif col[index]==-30.:
          curves.append(fits.Column("Linear ramp"+str(i)+str(index), np.array([-30., box.RStart, box.REnd,0.]), format='E'))
        else:
          Exception('You have an invalid setting for the value of the box associated with stage '+self.stages[i].name+', row '+str(index))
    return columns,curves,DIOstate
  
  