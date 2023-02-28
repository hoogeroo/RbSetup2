# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
try:
    import AIOUSB as da
except:
    pass
from matplotlib import cm, colors

import socket
TCP_IP = '130.216.51.242'
TCP_IP2= '130.216.51.179'
TCP_PORT = 8833
BUFFER_SIZE = 50

#def updatecolor(self):
#    cmap = cm.get_cmap(name='RdBu')
#    #only choose a number between 0.25 and 0.75
#    colrange=[0.25,0.75]
#    
#    value = self.value()
#    if value==0:
#        newcolor='#AAAAAA'
#    else:
#        valrange=[self.minimum(),self.maximum()]
#    
#        cmap_val = colrange[0] + colrange[1]*(value-valrange[0])/(valrange[1] - valrange[0])
#        newcolor=colors.rgb2hex(cmap(cmap_val))
#    
#    self.spin.setStyleSheet("QSpinBox"\
#                                "{"\
#                                f"background-color : {newcolor};"\
#                                "}")\

        

class LorentzDialog(QDialog):

    def __init__(self,parent):
        super(QDialog,self).__init__()
        self.lo=QGridLayout()
        self.Loffset=QDoubleSpinBox()
        self.Loffset.setValue(parent.LOffset)
        l1=QLabel("Offset")
        self.lo.addWidget(self.Loffset,0,1)
        self.lo.addWidget(l1,0,0)
        self.LAmp=QDoubleSpinBox()
        self.LAmp.setValue(parent.LAmp)
        l2=QLabel("Amplitude")
        self.lo.addWidget(self.LAmp,1,1)
        self.lo.addWidget(l2,1,0)
        self.LTc=QDoubleSpinBox()
        self.LTc.setValue(parent.LTc)
        self.LTc.setRange(0,10000)
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
        self.lo=QGridLayout()
        RStart=parent.RStart
        print(RStart)
        self.SB_RStart=QDoubleSpinBox()
        self.SB_RStart.setValue(RStart)
        l1=QLabel("Start Value")
        self.lo.addWidget(self.SB_RStart,0,1)
        self.lo.addWidget(l1,0,0)
        self.SB_REnd=QDoubleSpinBox()
        self.SB_REnd.setValue(parent.REnd)
        l2=QLabel("End Value")
        self.lo.addWidget(self.SB_REnd,1,1)
        self.lo.addWidget(l2,1,0)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.lo.addWidget(self.buttonBox)
        self.setLayout(self.lo)

class QMSbox(QDoubleSpinBox):
    def __init__(self,i,j):
        super(QMSbox,self).__init__()
        self.tid=j
        self.cid=i
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
        self.setDecimals(2)
        #self.setSingleStep(0.1)
        self.setToolTip('['+str(self.tid)+','+str(self.cid)+']')
        self.keepValue=0.0
        self.LAmp=0.0
        self.LOffset=0.0
        self.LTc=0.0
        self.RStart=0
        self.REnd=1
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
        self.setRange(0,5)
        self.setValue(self.keepValue)
        
    def RampAction(self):
        self.setRange(-30,30)
        if self.value()>-1:
            self.keepValue=self.value()
        self.setSpecialValueText("Ramp")
        self.setValue(-30)
        thisDialog=RampDialog(self)
        if thisDialog.exec_():
            self.RStart=thisDialog.SB_RStart.value()
            self.REnd=thisDialog.SB_REnd.value()
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
    
            cmap_val = colrange[0] + (colrange[1]-colrange[0])*(value-valrange[0])/(valrange[1] - valrange[0])
            newcolor=[int(np.ceil(255*x)) for x in cmap(cmap_val)]
    
        pal=self.palette()
        pal.setColor(QPalette.Base, QColor(newcolor[0],newcolor[1],newcolor[2]))
        self.setPalette(pal)

class Timebox(QDoubleSpinBox):
    def __init__(self):
        super(Timebox,self).__init__()
        self.setRange(0,20000)
        self.setDecimals(1)#self.setDecimals(0)#
        self.setSingleStep(0.1)

class DAC_Box(QMSbox):
    def __init__(self,i,j):
        super().__init__(i,j)
        self.DACid=j
        self.setRange(0,5)
        self.setSingleStep(0.1)
        self.valueChanged.connect(self.updatecolor)
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
        except:
            pass
    def convert(self):
        return self.value()
        #print(count,out,self.DACid)

class AOM_Freq_Box(QMSbox):
    def __init__(self,i,j,val=80):
        super().__init__(i,j)
        if (i<4):
          self.AOMid=j
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=j-4
          self.DDSid=1
          self.tcp=TCP_IP2
        self.setValue(val)
        self.setRange(55,105)
        self.setDecimals(0)
        self.valueChanged.connect(self.updatecolor)


class DC_AOM_Freq_Box(AOM_Freq_Box):
    def __init__(self,i,j,val=80):
        super(DC_AOM_Freq_Box,self).__init__(i,j)
        if (j<4):
          self.AOMid=j
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=j-4
          self.DDSid=1
          self.tcp=TCP_IP2
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
        if (j<4):
          self.AOMid=j
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=j-4
          self.DDSid=1
          self.tcp=TCP_IP2
        self.setValue(val)
        self.setRange(0,1)
        self.setSingleStep(0.05)
        self.valueChanged.connect(self.updatecolor)

class DC_AOM_Ampl_Box(AOM_Ampl_Box):
    def __init__(self,i,j,val=0.2):
        super().__init__(i,j,val=0.2)
        self.valueChanged.connect(self.update)
        self.setValue(val)
    def update(self):
        self.updatecolor()
        #print(self.value())
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.tcp, TCP_PORT))
            ml='AMPL,%d,%f' % (self.AOMid , (self.value()))
            #print(ml)
            s.send(ml.encode())
            s.recv(5)
            s.close()
        except:
            pass

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
