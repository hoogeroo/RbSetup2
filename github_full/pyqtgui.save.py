# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

@author: mhoo027
"""

import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt

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
        l3=QLabel("Time Constant")
        self.lo.addWidget(self.LTc,2,1)
        self.lo.addWidget(l3,2,0)
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
        self.keepValue=0.0
        self.LAmp=0.0
        self.LOffset=0.0
        self.LTc=0.0
        self.RStart=1.0
        self.REnd=0.0
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


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # creating EmailBlast widget and setting it as central
        #self.CW = spindemo(parent=self)
        self.CW = spindemo()
        self.setCentralWidget(self.CW)
        # filling up a menu bar
        bar = self.menuBar()
        bar.setNativeMenuBar(False)
        # File menu
        file_menu = bar.addMenu(' File')
        # adding actions to file menu
        open_action = QAction('Open', self)
        save_action = QAction('Save', self)
        close_action = QAction('Close', self)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(close_action)
        # Edit menu
        edit_menu = bar.addMenu(' Edit')
        # adding actions to edit menu
        undo_action = QAction('Undo', self)
        redo_action = QAction('Redo', self)
        add_action = QAction('Add Column on Right',self)
        insert_action = QAction('Insert Column before Cursor',self)
        remove_action= QAction('Remove Column at Cursor',self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(add_action)
        self.filename="default.fit"
        # use `connect` method to bind signals to desired behavior
        close_action.triggered.connect(self.close)
        save_action.triggered.connect(self.mysaveaction)
        open_action.triggered.connect(self.myopenaction)

    def myopenaction(self):
        if os.path.exists('defaultb.fit'):
            self.myload('defaultb.fit')

    def mysaveaction(self):
        if os.path.exists('defaultb.fit'):
            os.remove('defaultb.fit')
        self.mysave('defaultb.fit')

    def mysave(self,filename):
        from astropy.table import Table
        n=np.arange(100.0)
        Imhdu=fits.PrimaryHDU(n)
        prihdr=Imhdu.header
        ncols=self.CW.ntimes
        nrows=self.CW.nrows
        prihdr['NCOLS']=(ncols, 'Number of Columns')
        prihdr['NROWS']=(nrows, 'Number of Rows')
        prihdr['NDACS']=(self.CW.nDACs, 'Number of DACs')
        prihdr['NAOMS']=(self.CW.nAOMs, 'Number of AOMs')
        columns=[]
        rows=[]
        rows.append(0.0)
        for row in range(nrows):
            rows.append(self.CW.DCSpinboxes[row].value())
        columns.append(fits.Column('DC', array=np.array(rows), format='K'))
        for col in range(ncols):
            rows=[]
            rows.append(self.CW.Timeboxes[col].value())
            for row in range(nrows):
                rows.append(self.CW.Spinboxes[col][row].value())
            timeno='Time '+str(col)
            columns.append(fits.Column(timeno, array=np.array(rows), format='K'))
        Tabhdu=fits.BinTableHDU.from_columns(columns)
        curves=[]
        for i in range(ncols):
            for j in range(nrows):
                if (self.CW.Spinboxes[i][j].value() < -15.0):
                    pars=[]
                    if (self.CW.Spinboxes[i][j].value() == -20.0): ##Lorentzian
                        pars.append(-20.0)
                        pars.append(self.CW.Spinboxes[i][j].LOffset)
                        pars.append(self.CW.Spinboxes[i][j].LAmp)
                        pars.append(self.CW.Spinboxes[i][j].LTc)
                        curves.append(fits.Column("Lorentz",array=np.array(pars), format='K'))
                    if (self.CW.Spinboxes[i][j].value() == -30.0): ##Linear ramp
                        pars.append(-30.0)
                        pars.append(self.CW.Spinboxes[i][j].RStart)
                        pars.append(self.CW.Spinboxes[i][j].REnd)
                        pars.append(0.0)
                        curves.append(fits.Column("Linear ramp",array=np.array(pars), format='K'))
        Tab2hdu=fits.BinTableHDU.from_columns(curves)
        hdu1=fits.HDUList([Imhdu,Tabhdu,Tab2hdu])
        hdu1.writeto(filename)

    def myload(self,filename):
        from astropy.table import Table
        fitsfile=fits.open(filename)
        headers=fitsfile[0].header
        ncols=headers['NCOLS']
        nrows=headers['NROWS']
        tabledata=fitsfile[1].data
        curvedata=fitsfile[2].data
        myid=0
        for row in range(nrows):
            self.CW.DCSpinboxes[row].setValue(tabledata[row][0])
        for col in range(ncols):
            coln=col+1
            self.CW.Timeboxes[col].setValue(tabledata[0][coln])
            for row in range(nrows):
                tmp=tabledata[row+1][coln]
                if tmp<-10:
                    print('bpp')
                    self.CW.Spinboxes[col][row].setRange(tmp,10.0)
                    if ((tmp<-15) and (tmp>-25)):
                        self.CW.Spinboxes[col][row].LOffset=curvedata[1][myid]
                        self.CW.Spinboxes[col][row].LAmp=curvedata[2][myid]
                        self.CW.Spinboxes[col][row].LTc=curvedata[3][myid]
                        self.CW.Spinboxes[col][row].setSpecialValueText("Lrtz")
                        print('bxx')
                    if ((tmp<-25) and (tmp>-35)):
                        self.CW.Spinboxes[col][row].RStart=curvedata[1][myid]
                        self.CW.Spinboxes[col][row].REnd=curvedata[2][myid]
                        self.CW.Spinboxes[col][row].setSpecialValueText("Ramp")
                        print('byy')
                    myid=myid+1
                self.CW.Spinboxes[col][row].setValue(tmp)
        fitsfile.close()



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

def main():
   app = QApplication(sys.argv)
   mw = MainWindow()
   #ex = spindemo()
   mw.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
