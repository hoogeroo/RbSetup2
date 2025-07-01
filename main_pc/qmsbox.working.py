# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import AIOUSB as da

import socket
TCP_IP = '130.216.51.242'
TCP_IP2= '130.216.51.179'
TCP_PORT = 8833
BUFFER_SIZE = 50


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
        #self.setSingleStep(0.1)
        self.setToolTip('['+str(self.tid)+','+str(self.cid)+']')
        self.keepValue=0.0
        self.LAmp=0.0
        self.LOffset=0.0
        self.LTc=0.0
        self.RStart=1.0
        self.REnd=0.0
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
        self.setRange(-10.1,10)
        self.setValue(self.keepValue)
    def RampAction(self):
        self.setRange(-30,30)
        self.keepValue=self.value()
        self.setSpecialValueText("Ramp")
        self.setValue(-30)
        thisDialog=RampDialog(self)
        if thisDialog.exec_():
            self.RStart=thisDialog.SB_RStart.value()
            self.REnd=thisDialog.SB_REnd.value()
            #print(self.RStart)
        else:
            self.ConstantAction()

class Timebox(QDoubleSpinBox):
    def __init__(self):
        super(Timebox,self).__init__()
        self.setRange(0,10000)


class DAC_Box(QMSbox):
    def __init__(self,i,j):
        super(DAC_Box,self).__init__(i,j)
        self.DACid=i
        self.setRange(0,5)
        self.setSingleStep(0.1)
        self.valueChanged.connect(self.updatecolor)
    def updatecolor(self):
        p=self.palette()
        a=self.value()
        if a<0:
            b=self.minimum()
            mycolour=QColor.fromRgbF(a/b,0,0)
        else:
            b=self.maximum()
            mycolour=QColor.fromRgbF(0,0,a/b)
        p.setColor(self.backgroundRole(),mycolour)
        self.setPalette(p)

class DC_DAC_Box(DAC_Box):
    def __init__(self,i):
        super(DC_DAC_Box,self).__init__(i,0)
        self.valueChanged.connect(self.updateDAC)
    def updateDAC(self):
        #print(self.parent())
        #da=self.parent().da
        #EDRE.writeChannel(0,self.DACid,int(self.value()*1000000))
        fullscale=5.0
        count=np.ushort(self.value()/fullscale*0xfff)
        #did=np.ushort(self.DACid)
        out=da.DACDirect(0,self.DACid,count)
        #print(count,out,self.DACid)

class AOM_Freq_Box(QDoubleSpinBox):
    def __init__(self,i):
        super(AOM_Freq_Box,self).__init__()
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
        self.setValue(80)
        self.setRange(55,105)
       

class DC_AOM_Freq_Box(AOM_Freq_Box):
    def __init__(self,i):
        super(AOM_Freq_Box,self).__init__()
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
        self.setValue(80)
        self.setRange(55,105)
        self.valueChanged.connect(self.update)
    def update(self):
        #print(self.value())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.tcp, TCP_PORT))
        ml='FREQ,%d,%f' % (self.AOMid , (self.value()))
        #print(ml)
        s.send(ml.encode())
        s.recv(5)
        s.close()

class DC_DIO_Box(QCheckBox):
    def __init__(self,i):
        self.DIOid=i
        self.stateChanged.connect(self.update)
    def update(self):
        if self.checkState():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.connect((TCP_IP, TCP_PORT))
            #ml='AMPL,%d,%f' % (self.AOMid , (self.value()))
            ##print(ml)
            #s.send(ml.encode())
            #s.recv(5)
            #s.close()

class AOM_Ampl_Box(QDoubleSpinBox):
    def __init__(self,i):
        super(AOM_Ampl_Box,self).__init__()
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
        self.setValue(0.0)
        self.setRange(0,1)
        self.setSingleStep(0.05)

class DC_AOM_Ampl_Box(AOM_Ampl_Box):
    def __init__(self,i):
        super(AOM_Ampl_Box,self).__init__()
        if (i<4):
          self.AOMid=i
          self.DDSid=0
          self.tcp=TCP_IP
        else:
          self.AOMid=i-4
          self.DDSid=1
          self.tcp=TCP_IP2
        self.setValue(1)
        self.setRange(0,1)
        self.setSingleStep(0.05)
        self.valueChanged.connect(self.update)
    def update(self):
        #print(self.value())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.tcp, TCP_PORT))
        ml='AMPL,%d,%f' % (self.AOMid , (self.value()))
        #print(ml)
        s.send(ml.encode())
        s.recv(5)
        s.close()

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
