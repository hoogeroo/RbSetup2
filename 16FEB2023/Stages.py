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

#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================

class Stages():
  def __init__(self,devdict=None, stagenames=None, table=None, curves=None, DIOstate=None, nstages=8):
    self.devices=devdict
    self.devIDs=dict()
    total=0
    for key in self.devices.keys():
        self.devIDs[key]=list(range(total,total+len(self.devices[key])))
        total+=len(self.devices[key])
        
    self.stages=[]
    self.DC=[]
    
    if not type(table)=='NoneType':
      DIOstate=np.asarray(DIOstate)
      self.populate(table,curves,DIOstate,stagenames)

    else:
      self.addDC()
      for i in range(nstages):
        self.addStage()
        
    #==============================================================================================================
    #==============================================================================================================

  def addDC(self,vals=None,DIOstate=None):
    n=len(self.devices['DAC'])
    for devtype, devices in self.devices.items():
      if devtype=='DAC':
        for i in range(len(devices)):
          self.DC.append(DC_DAC_Box(1,i))
          if vals:
            self.DC[-1].setValue(vals[i])
      elif devtype=='DIO':
        for i in range(len(devices)):
          self.DC.append(DC_DIO_Box(i))
          if not type(DIOstate)=='NoneType':
            self.DC[-1].setChecked(DIOstate[i])
      elif devtype=='AOM':
        for i in range(len(devices)):
            j=i//2
            if not type(vals)=='NoneType':
                if not i%2:
                    self.DC.append(DC_AOM_Freq_Box(1,j,val=vals[n+i]))
                else:
                    self.DC.append(DC_AOM_Ampl_Box(1,j,val=vals[n+i]))
            else:
                if not i%2:
                    self.DC.append(DC_AOM_Freq_Box(1,j))
                else:
                    self.DC.append(DC_AOM_Ampl_Box(1,j))  
      elif devtype != 'EagleDAC':
        Exception('Too many different device types!')
        
    #==============================================================================================================
    #==============================================================================================================

  def addStage(self,time=0,name=None,vals=None,DIOstate=None,position='last'):
    stageid = len(self.stages)
    if name:
      newname=name
    else:
      newname = 'Stage '+str(stageid)
    self.stages.append(newStage(newname,stageid, time, self.devices))
    
    valcount=0
    iocount=0
    stagevals=self.stages[-1].boxes
    for i in range(len(stagevals)):
      if isinstance(stagevals[i], QCheckBox):
        DIOval=False
        if DIOstate:
          DIOval = DIOstate[iocount]
        stagevals[i].setChecked(DIOval)
        iocount+=1
      elif vals:
        stagevals[i].setValue(vals[valcount])
        valcount+=1
                     
    self.moveStage(position=position)
        #self.stages = [self.stages[:position],self.stages[-1], self.stages[position:-1]]
        
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

  def moveStage(self,a=-1,position='last'):
    stageid = len(self.stages)
    if a=='last' or a >= stageid or a < 0:
      a=-1
    if position=='last' or position >= stageid or position < 0:
      position=stageid
    if not a==position:  
      self.stages.insert(position, self.stages.pop(a))   
      
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
   
  def delStage(self,position='last'):
    if position == 'last' or position > len(self.stages):
      del self.stages[-1]
    else:
      del self.stages[position]
      
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
  def dupStage(self,a,position='last'):
    stagecopy=self.stages[a]
    values = [x.value() for x in stagecopy.boxes if not isinstance(x,QCheckBox)]
    DIOstate = [x.isChecked() for x in stagecopy.boxes if isinstance(x,QCheckBox)]
    
    self.addStage(time=stagecopy.time.value(), vals=values,DIOstate=DIOstate, position=position)
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
  def swapStage(self,a,b):
    self.stages[a], self.stages[b] = self.stages[b], self.stages[a]
    
  def updateorder(self,neworder):
    self.stages=self.stages[neworder]
    
    #==============================================================================================================
    #==============================================================================================================

    
  def populate(self, table,curves,DIOstate=None,names=None):
    DIOstate = np.asarray(DIOstate)
    for i in self.stages:
      self.delStage()
      
    dc_vals = [table[i][0] for i in range(1,len(table))]
    
    if DIOstate.size:
      dc_dio = DIOstate[:][0]
    else:
      dc_dio=[]
    self.addDC(vals=dc_vals,DIOstate=dc_dio)
    
    if names:
        names.insert(0,0)
        
    for j in range(1,len(table[0])):
      DIOj=[]
      if DIOstate.size:
        DIOj=[DIOstate[x][j] for x in range(len(self.devices['DIO']))]
      valtab = [table[x][j] for x in range(1,len(table))] 
      if names:
        newname=names[j]
      else:
        newname=[]
      self.addStage(name=newname, time=table[0][j],vals=valtab,DIOstate=DIOj)
    
    if len(curves.names)>1:
      for k,curve in enumerate(curves):
        #print(curve)
        namestr = curve.names[k]
        name=namestr.split()
        vals = [data[0] for data in curve]
        
        box = self.stages[int(name[1])].boxes[int(name[2])]
        box.setValue(vals[0])
        
        if name[0] == 'Linear_ramp':
          box.setRange(-30,30)
          box.setSpecialValueText("Ramp")
          box.RStart = vals[1]; box.REnd = vals[2]
        elif name[0] == 'Lorentz':
          box.setRange(-20,20)
          box.setSpecialValueText("Lrtz")
          box.Loffset = vals[1]; box.LAmp = vals[2]; box.LTc = vals[3]
    elif len(curves.names)==1:
      namestr = curves.names[0]
      name=namestr.split()
      vals = [data[0] for data in curves]
      
      box = self.stages[int(name[1])].boxes[int(name[2])]
      
      if name[0] == 'Linear_ramp':
        box.setRange(-30,30)
        box.setValue(int(vals[0]))
        box.setSpecialValueText("Ramp")
        box.RStart = vals[1]; box.REnd = vals[2]
      elif name[0] == 'Lorentz':
        box.setRange(-20,20)
        box.setValue(int(vals[0]))
        box.setSpecialValueText("Lrtz")
        box.Loffset = vals[1]; box.LAmp = vals[2]; box.LTc = vals[3]
     
    #==============================================================================================================
    #==============================================================================================================

  def store(self):
    columns=[]
    curves=[]
    DIOstate=[]
    
    DC_vals = [x.value() for x in self.DC if not isinstance(x, QCheckBox)]
    DC_vals.insert(0,0.0)
    columns.append(fits.Column('DC'+str(len(DC_vals)-1), array=np.array(DC_vals), format='E'))
    
    DC_DIOval=[x.isChecked() for x in self.DC if isinstance(x,QCheckBox)]
    DIOstate.append(fits.Column('DCDIO', array=np.array(DC_DIOval), format='E'))
    
    for i in range(len(self.stages)):
      DIOval=[]
      col=[box.value() for box in self.stages[i].boxes if not isinstance(box, QCheckBox)]
      col.insert(0,self.stages[i].time.value())
      columns.append(fits.Column(self.stages[i].name, array=np.array(col), format='E'))
      
      DIOval=[box.isChecked() for box in self.stages[i].boxes if isinstance(box,QCheckBox)]
      DIOstate.append(fits.Column('TimeDIO '+str(i), array=np.array(DIOval), format='E'))
      
      linramps=[[i, j, -30., box.RStart, box.REnd, 0.] for j, box in enumerate(self.stages[i].boxes) if (not isinstance(box, QCheckBox))and(int(box.value())==-30)]
      #print(linramps)
      
      lorramps = [[i, j, -20., box.Loffset, box.LAmp, box.LTc] for j, box in enumerate(self.stages[i].boxes) if (not isinstance(box, QCheckBox))and(int(box.value())==-20)]
      #print(lorramps)
      
      for ramp in linramps:
        curves.append(fits.Column(f'Linear_ramp {ramp[0]} {ramp[1]}', array=np.array(ramp[2:]), format='E'))
      
      for ramp in lorramps:
        curves.append(fits.Column(f'Lorentz {ramp[0]} {ramp[1]}', array=np.array(ramp[2:]), format='E'))
      #indices = np.where(np.array(col) < -15)
      #if indices:
      #  print(indices)
     
      #for index in indices:
      #  if index:
          #index=int(index)
          #box=self.stages[i].boxes[index]
          #print(box.value())
          #print(box.RStart, box.REnd)
          #if col[index]==-20.:
            #curves.append(fits.Column(f'Lorentz {str(i)} {str(index)}', array=np.array([-20., box.Loffset, box.LAmp, box.LTc]), format='E'))
          #elif col[index]==-30.:
            #curves.append(fits.Column(f'Linear_ramp {str(i)} {str(index)}', array=np.array([-30., box.RStart, box.REnd,0.]), format='E'))
            #print(curves[-1])
          #else:
            #Exception('You have an invalid setting for the value of the box associated with stage '+self.stages[i].name+', row '+str(index))
    return columns,curves,DIOstate
  
#==============================================================================================================
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
#==============================================================================================================

class newStage():
  def __init__(self,name,stageid, t,devdict):
    self.name=name
    self.sID = stageid
    self.time=Timebox()
    self.time.setValue(t)
    self.boxes=[]
    for devtype, devices in devdict.items():
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
 