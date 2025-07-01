# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# PACKAGE IMPORTS
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import socket

from matplotlib import cm, colors
from functools import partial

# Our imports
from dacprops import *
try:
    import AIOUSB as da
except:
    pass
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

TCP_IP = '130.216.51.242'
TCP_IP2= '130.216.51.179'
TCP_PORT = 8833
BUFFER_SIZE = 50

rframpID = 7

class QMSbox(QDoubleSpinBox):
    def __init__(self,i,j):
        super(QMSbox,self).__init__()
        self.tid=j
        self.cid=i
        self.rightclick_enabled = True
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
        self.setDecimals(2)
        #self.setSingleStep(0.1)
        self.setToolTip('['+str(self.tid)+','+str(self.cid)+']')
        self.keepValue=0.0
        
        self.LAmp=0.0
        self.LOffset=0.0
        self.LTc=0.0
        
        self.RStart=0; self.Rmin = 0
        self.REnd=1; self.Rmax = 5
        
        self.updatecolor()
        #self.setFont(QFont('Arial',7))
        
    def valuechange(self):
        print(self.tid,self.cid,self.value())
    def popmenu(self):
        print("Thepop")
    #def mousePressEvent(self, QMouseEvent):
    #    if QMouseEvent.button() == Qt.LeftButton:
    #        print("Left Button Clicked")
    #    elif QMouseEvent.button() == Qt.RightButton:
    #        #do what you want here
    #        print("Right Button Clicked")
    def __contextMenu(self):
        if self.rightclick_enabled:
          self._normalMenu = self.OpenMenu()
          self._normalMenu.exec_(QCursor.pos())
        
    def OpenMenu(self):
        print("This")
        self.menu=QMenu(self)
        self.cAction=QAction("Constant")
        self.menu.addAction(self.cAction)
        self.lAction=QAction("Linear Ramp")
        self.menu.addAction(self.lAction)
        self.eAction=QAction("Exponential curve")
        self.menu.addAction(self.eAction)
        self.zAction=QAction("Lorentzian curve")
        self.menu.addAction(self.zAction)
        self.zAction.triggered.connect(self.Lorentzaction)
        self.cAction.triggered.connect(self.ConstantAction)
        self.lAction.triggered.connect(self.RampAction)
        #action = menu.exec_(self.mapToGlobal(position))
        return self.menu
      
    def Lorentzaction(self):
        self.setRange(-20,20)
        if self.value()>-1:
            self.keepValue=self.value()
        self.setValue(-20)
        self.setSpecialValueText("Lrtz")
        self.menu.setVisible(False)
        thisDialog=LorentzDialog(self)
        if thisDialog.exec_():
            self.LOffset=thisDialog.Loffset.value()
            #print(self.Loffset)
            self.LAmp=thisDialog.LAmp.value()
            self.LTc=thisDialog.LTc.value()
            
    def ConstantAction(self):
        #dac_conversions[self.cid].minv, .maxv (see dacprops.py)
        self.setSpecialValueText('')
        self.setRange(self.Rmin, self.Rmax)#dac_conversions[self.cid].minv, dac_conversions[self.cid].maxv)
        self.setValue(self.keepValue)
        
    def RampAction(self):
        self.setRange(-30,30)
        if self.value()>-1:
            self.keepValue=self.value()
        self.setSpecialValueText("Ramp")
        self.setValue(-30)
        thisDialog=RampDialog(self)
        if thisDialog.exec_():
            self.RStart = thisDialog.SB_RStart.value()
            self.REnd = thisDialog.SB_REnd.value()
            #print(self.RStart, self.REnd)
            #print(self.RStart)
        else:
            self.ConstantAction()
            
    def updatecolor(self):
        cmap = cm.get_cmap(name='RdBu')#'Spectral')#
        #only choose a number between 0.25 and 0.75
        colrange=[0.25,0.75]
    
        value = self.value()
        if value==0:
            newcolor=3*[180]#[128,128,128]#'#AAAAAA'
        else:
            valrange=[self.minimum(),self.maximum()]
            try:
              cmap_val = colrange[0] + (colrange[1]-colrange[0])*(value-valrange[0])/(valrange[1] - valrange[0])
            except:
              cmap_val = 0.5
            newcolor=[int(np.ceil(255*x)) for x in cmap(cmap_val)]
    
        pal=self.palette()
        pal.setColor(QPalette.Base, QColor(newcolor[0],newcolor[1],newcolor[2]))
        self.setPalette(pal)
        #try:
        #  print(f'DAC ID:{self.DACid} - value changed to {self.value()}')
        #except Exception as e:
        #  print(e)

class Timebox(QDoubleSpinBox):
    def __init__(self):
        super(Timebox,self).__init__()
        self.setRange(0,20000)
        self.setDecimals(1)#self.setDecimals(0)#
        self.setSingleStep(0.1)

class DAC_Box(QMSbox):
    def __init__(self,i,cid):
        super().__init__(i,cid)
        self.DACid=cid
        #self.setRange(0,5)
        self.adjustrange(dac_conversions[cid].minv, dac_conversions[cid].maxv)
        self.setSingleStep(dac_conversions[cid].step)
        self.valueChanged.connect(self.updatecolor)
        #self.Rmin = dac_conversions[self.DACid].minv # Now handled within adjustrange
        #self.Rmax = dac_conversions[self.DACid].maxv
        
    def adjustrange(self, low, high):
        bot = min([low, high]); top = max([low, high])
        #print(f'Device: {self.DACid} - range={[bot, top]}')
        if self.DACid == rframpID and low != high:
          dac_conversions[rframpID].minv = bot; dac_conversions[rframpID].maxv = top
          dac_conversions[rframpID].pars[0] = -5*bot / (top - bot)
          dac_conversions[rframpID].pars[1] = 5/(top - bot); 
        if self.value() > -1:
            self.setRange(bot, top)
            val = self.value()
            #for val in [rstart, rend]: # This moves moves each start/end value within the allowed range
            val = min([val, top])
            val = max([val, bot])
            self.setValue(val)
        self.Rmin = bot; self.Rmax = top
        self.updatecolor()
        
    def convert(self):
        out=dac_conversions[self.DACid].getval(self.value())
        #print(out)
        return out
    #def updatecolor(self):
    #    p=self.palette()
    #    a=self.value()
    #    if a<0:
    #        b=self.minimum()
    #        mycolour=QColor.fromRgbF(a/b,0,0)
    #    else:
    #        b=self.maximum()
    #        mycolour=QColor.fromRgbF(0,0,a/b)
    #    p.setColor(self.backgroundRole(),mycolour)
    #    self.setPalette(p)

class DC_DAC_Box(DAC_Box):
    def __init__(self,i,j):
        super().__init__(i,j)
        self.valueChanged.connect(self.updateDAC)
    def updateDAC(self):
        self.updatecolor()
        #print(self.parent())
        #da=self.parent().da
        #EDRE.writeChannel(0,self.DACid,int(self.value()*1000000))
        fullscale=5.0
        #print("I'm here\n",self.DACid)
        count=np.ushort(self.convert()/fullscale*0xfff)
        #did=np.ushort(self.DACid)
        try:
            out=da.DACDirect(0,self.DACid,count)
            #print("DC DAC updated")
        except:
            print("Issues updating DAC")
            pass
   
        #print(count,out,self.DACid)

class AOM_Freq_Box(QMSbox):
    def __init__(self,i,j,val=80):
        super().__init__(i,j)
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
          
        self.rightclick_enabled = False
        
        self.setValue(val)
        self.setRange(55,105)
        self.setDecimals(0)
        self.valueChanged.connect(self.updatecolor)


class DC_AOM_Freq_Box(AOM_Freq_Box):
    def __init__(self,i,j,val=80):
        super(DC_AOM_Freq_Box,self).__init__(i,j)
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
          
        self.rightclick_enabled = False
        
        self.setValue(val)
        self.setRange(55,105)
        self.valueChanged.connect(self.update)
    def update(self):
        self.updatecolor()
        #print(self.value())
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.tcp, TCP_PORT))
            ml='FREQ,%d,%f' % (self.AOMid , (self.value()))
            #print(ml)
            s.send(ml.encode())
            s.recv(5)
            s.close()
        except:
            pass

class DC_DIO_Box(QCheckBox):
    def __init__(self,i):
        super().__init__()
        self.DIOid=i
        self.stateChanged.connect(self.update)
    def update(self):
        if self.checkState():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TCP_IP, TCP_PORT))
            #ml='AMPL,%d,%f' % (self.AOMid , (self.value()))
            ml="DCTRIG,%d,ON" % self.DIOid
            print(ml)
            s.send(ml.encode())
            #s.recv(5)
            s.close()
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TCP_IP, TCP_PORT))
            #ml='AMPL,%d,%f' % (self.AOMid , (self.value()))
            ml="DCTRIG,%d,OFF" % (self.DIOid)
            print(ml)
            s.send(ml.encode())
            #s.recv(5)
            s.close()

class AOM_Ampl_Box(QMSbox):
    def __init__(self,i,j,val=0.2):
        super().__init__(i,j)
        self.convert_index = i
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
        
        self.rightclick_enabled = (self.AOMid == 3) or (i==4) # automatically disables context menu unless we're looking at the final AOM where ramping is allowed!
        
        
        
        self.setValue(val)
        #self.setRange(0,1)
        self.adjustrange(aom_amp_conversions[self.convert_index].minv, \
                         aom_amp_conversions[self.convert_index].maxv)
        #self.setRange(aom_amp_conversions[self.convert_index].minv, \
        #              aom_amp_conversions[self.convert_index].maxv)
        #self.setSingleStep(0.05)
        self.setSingleStep(aom_amp_conversions[self.convert_index].step)
        self.valueChanged.connect(self.updatecolor)
        
        #self.setRange(dac_conversions[j].minv,dac_conversions[j].maxv)
        #self.setSingleStep(dac_conversions[j].step)
        #self.valueChanged.connect(self.updatecolor)
        
        #self.Rmin = aom_amp_conversions[self.convert_index].minv # now handled in adjustrange
        #self.Rmax = aom_amp_conversions[self.convert_index].maxv
    def adjustrange(self, low, high):
        self.setRange(low, high)
        self.Rmin = low; self.Rmax = high
        self.updatecolor()
        
    def convert(self):
        out=aom_amp_conversions[self.convert_index].getval(self.value())
        #print(out)
        return out

class DC_AOM_Ampl_Box(AOM_Ampl_Box):
    def __init__(self,i,j,val=0.2):
        super().__init__(i,j,val=0.2)
        self.valueChanged.connect(self.update)
        self.setValue(val)
        self.rightclick_enabled = False
    def update(self):
        self.updatecolor()
        #print(self.value())
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.tcp, TCP_PORT))
            ml='AMPL,%d,%f' % (self.AOMid , (self.convert()))
            #print(ml)
            s.send(ml.encode())
            s.recv(5)
            s.close()
        except:
            pass

class LorentzDialog(QDialog):
    def __init__(self,parent):
        super(QDialog,self).__init__()
        self.lo=QGridLayout()
        self.Loffset=QDoubleSpinBox()
        self.Loffset.setRange(parent.Rmin,parent.Rmax)
        self.Loffset.setValue(parent.LOffset)
        l1=QLabel("Offset")
        self.lo.addWidget(self.Loffset,0,1)
        self.lo.addWidget(l1,0,0)
        self.LAmp=QDoubleSpinBox()
        self.LAmp.setRange(parent.Rmin,parent.Rmax)
        self.LAmp.setValue(parent.LAmp)
        l2=QLabel("Amplitude")
        self.lo.addWidget(self.LAmp,1,1)
        self.lo.addWidget(l2,1,0)
        self.LTc=QDoubleSpinBox()
        self.LTc.setValue(parent.LTc)
        self.LTc.setRange(0.1,10000)
        l3=QLabel("Time Constant")
        self.lo.addWidget(self.LTc,2,1)
        self.lo.addWidget(l3,2,0)
        self.cbRising=QCheckBox()
        self.lo.addWidget(self.cbRising,3,1)
        self.lRising=QLabel('Rising')
        self.lo.addWidget(self.lRising,3,0)
        self.cbRising.setChecked(False)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.lo.addWidget(self.buttonBox)
        self.setLayout(self.lo)

class RampDialog(QDialog):
    def __init__(self,parent):
        super(QDialog,self).__init__()
        self.Rmin = parent.Rmin#dac_conversions[parent.cid].minv
        self.Rmax = parent.Rmax#dac_conversions[parent.cid].maxv
        #print(f'Rmin = {self.Rmin}; Rmax = {self.Rmax}')
        
        self.lo=QGridLayout()
        
        #print(parent.RStart)
        rstart = parent.RStart; rend = parent.REnd 
        for val in [rstart, rend]: # This moves moves each start/end value within the allowed range
          val = min([val, self.Rmax])
          val = max([val, self.Rmin])
        
        self.SB_RStart=QDoubleSpinBox()
        self.SB_RStart.setRange(self.Rmin, self.Rmax)
        self.SB_RStart.setValue(rstart)
        l1=QLabel("Start Value")
        self.lo.addWidget(self.SB_RStart,0,1)
        self.lo.addWidget(l1,0,0)
        
        self.SB_REnd=QDoubleSpinBox()
        self.SB_REnd.setRange(self.Rmin, self.Rmax)
        self.SB_REnd.setValue(rend)
        l2=QLabel("End Value")
        self.lo.addWidget(self.SB_REnd,1,1)
        self.lo.addWidget(l2,1,0)
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.lo.addWidget(self.buttonBox)
        self.setLayout(self.lo)

def main():
   app = QApplication(sys.argv)
   mw = MainWindow()
   #ex = spindemo()
   mw.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   #main()
   da.GetDevices()
   print(da.DACDirect(0,0,500))
