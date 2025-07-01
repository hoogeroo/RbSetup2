#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 12:23:43 2019

@author: lab
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from DAQ import *

from networkDDS import *

class AnalogEntry(QtWidgets.QWidget):
        
    valueChanged = QtCore.pyqtSignal(int, int, name='valueChanged')
        
    def __init__(self,channel,analogLine, parent = None):
        super(AnalogEntry,self).__init__(parent)     
        
        self.channel = channel
        
        self.parent = parent
        
        self.analogLine = analogLine
        
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(0,0,80,20))
        self.lbChannel.setText(self.analogLine.label)
        self.lbChannel.setObjectName("lbChannel")
        self.sbValue = QtWidgets.QSpinBox(self)
        self.sbValue.setGeometry(QtCore.QRect(90,0,100,20))
        self.sbValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbValue.setMinimum(self.analogLine.min_val)
        self.sbValue.setMaximum(self.analogLine.max_val)
        self.sbValue.setSingleStep(self.analogLine.increment)
        self.sbValue.setValue(self.analogLine.default)
        self.sbValue.setObjectName("sbValue")
        self.lbUnits = QtWidgets.QLabel(self)
        self.lbUnits.setGeometry(QtCore.QRect(200,0,40,20))
        self.lbUnits.setText(self.analogLine.units)

        self.sbValue.valueChanged.connect(self.changeValue)
        QtCore.QMetaObject.connectSlotsByName(self)

    def getValue(self):
        return self.sbValue.value()
        
    def changeValue(self,value):
        if value < self.analogLine.min_val:
            value = self.analogLine.min_val
        elif value > self.analogLine.max_val:
            value = self.analogLine.max_val
            
        self.sbValue.setValue(value)
                
        self.valueChanged.emit(self.channel,value)
        
class DigitalEntry(QtWidgets.QWidget):
        
    valueChanged = QtCore.pyqtSignal(int, int, name='valueChanged')
        
    def __init__(self,channel,digitalLine, parent = None):
        super(DigitalEntry,self).__init__(parent)        
        self.channel = channel
        
        self.parent = parent
        
        self.digitalLine = digitalLine
        
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(0,0,80,20))
        self.lbChannel.setText(self.digitalLine.label)
        self.lbChannel.setObjectName("lbChannel")
#        self.gbDigitalValue = QtWidgets.QGroupBox(self)
#        self.gbDigitalValue.setGeometry(QtCore.QRect(70, 0, 300, 40))
#        self.gbDigitalValue.setObjectName("gbDigitalValue")
        self.rbDigitalZero = QtWidgets.QRadioButton(self)
        self.rbDigitalZero.setGeometry(QtCore.QRect(90, 0, 50, 20))
        self.rbDigitalZero.setChecked(not self.digitalLine.default)
        self.rbDigitalZero.setText("Off")
        self.rbDigitalZero.setObjectName("rbDigitalZero")
        self.rbDigitalOne = QtWidgets.QRadioButton(self)
        self.rbDigitalOne.setGeometry(QtCore.QRect(150, 0, 50, 20))
        self.rbDigitalOne.setText("On")
        self.rbDigitalOne.setChecked(self.digitalLine.default)
        self.rbDigitalOne.setObjectName("rbDigitalOne")
        
#        self.loDigital = QtWidgets.QHBoxLayout(self)
#        self.loDigital.addWidget(self.rbDigitalZero)
#        self.loDigital.addWidget(self.rbDigitalOne)
#        self.loDigital.addStretch(1)
#        self.gbDigitalValue.setLayout(self.loDigital)

        self.rbDigitalZero.toggled.connect(self.zeroSet)
        self.rbDigitalOne.toggled.connect(self.oneSet)
        QtCore.QMetaObject.connectSlotsByName(self)
 
    def zeroSet(self):
        if self.rbDigitalZero.isChecked():
            self.rbDigitalOne.setChecked(False)
        else:
            self.rbDigitalOne.setChecked(True)
        
        self.toggleValue()
        
    def oneSet(self):
        if self.rbDigitalOne.isChecked():
            self.rbDigitalZero.setChecked(False)
        else:
            self.rbDigitalZero.setChecked(True)
            0
        self.toggleValue()

    def getValue(self):
        return self.rbDigitalOne.isChecked()
        
    def changeValue(self,value):
        if value:
            val = self.digitalLine.on_value
        else:
            val = self.digitalLine.off_value
            
        self.valueChanged.emit(self.channel,val)
    
    def toggleValue(self):
        if self.rbDigitalOne.isChecked():
            value = self.digitalLine.on_value
        else:
            value = self.digitalLine.off_value
                
        self.valueChanged.emit(self.channel,value)

class NetworkEntry(QtWidgets.QWidget):
        
    valueChanged = QtCore.pyqtSignal(int, int, int, float, name='valueChanged')
        
    def __init__(self,channel,networkLine, parent = None):
        super(NetworkEntry,self).__init__(parent)
        
        self.channel = channel
        
        self.parent = parent
        
        self.networkLine = networkLine
        
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(0,0,80,20))
        self.lbChannel.setText(self.networkLine.label)
        self.lbChannel.setObjectName("lbChannel")
        self.wNetworkDDS = networkDDS(channel,self.networkLine.labels,self)
        self.wNetworkDDS.setGeometry(QtCore.QRect(0, 20, 400,80))
        self.wNetworkDDS.setObjectName("wNetworkDDS")

        self.wNetworkDDS.frequencyChanged.connect(lambda subchannel,value : self.changeValue(subchannel,0,value))
        self.wNetworkDDS.amplitudeChanged.connect(lambda subchannel,value : self.changeValue(subchannel,1,value))
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def getValue(self,subchannel,function):
        if function == 0:
            return self.wNetworkDDS.channels[subchannel].getFrequency()
        else:
            return self.wNetworkDDS.channels[subchannel].getAmplitude()
    
    def changeValue(self,subchannel,function,value):
        if function == 0:
            self.wNetworkDDS.channels[subchannel].setFrequency(value)
        else:
            self.wNetworkDDS.channels[subchannel].setAmplitude(value)

        self.valueChanged.emit(self.channel,subchannel,function,value)
        
class DirectControl(QtWidgets.QWidget):
    def __init__(self,mainWindow,parent = None):
        super(DirectControl,self).__init__(parent)
        
        self.mainWindow = mainWindow
        
        self.parent = parent
        
        chan, subchan = daq.getChannelNumber("Push Beam")
        
        self.pushBeamChannel = chan.value()
        self.pushBeamSubChannel = subchan.value()
        
        self.mot1val = 0
        
        self.freq_min_val = daq.lines[self.pushBeamChannel].freq_min
        self.freq_max_val = daq.lines[self.pushBeamChannel].freq_max
        self.freq_increment = daq.lines[self.pushBeamChannel].freq_increment
        self.freq_default = daq.lines[self.pushBeamChannel].freq_default

        self.amp_min_val = daq.lines[self.pushBeamChannel].amp_min
        self.amp_max_val = daq.lines[self.pushBeamChannel].amp_max
        self.amp_increment = daq.lines[self.pushBeamChannel].amp_increment
        self.amp_default = daq.lines[self.pushBeamChannel].amp_default

        self.setObjectName("Form")
        self.resize(400, 900)
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(20, 10, 60, 20))
        self.lbChannel.setObjectName("lbChannel")
        self.lbValue = QtWidgets.QLabel(self)
        self.lbValue.setGeometry(QtCore.QRect(90, 10, 300, 20))
        self.lbValue.setObjectName("lbValue")

        self.analogLines = {}
        self.digitalLines = {}
        self.networkLines = {}
        
        self.column = 0
        self.cursor = 30

        for ii in range(daq.analog_outputs):
            self.analogLines[ii] = AnalogEntry(ii,daq.lines[ii],self)
            self.analogLines[ii].setGeometry(QtCore.QRect(self.column*350+20, self.cursor, 300, 20))
            self.analogLines[ii].setObjectName("analogLine"+str(ii))
            
            self.analogLines[ii].valueChanged.connect(lambda channel, value: self.changeAnalog(channel,value))
            
            self.cursor += 20
            
        self.column = 1    
        self.cursor = 30
        
        for ii in range(daq.digital_outputs):
            jj = ii + daq.analog_outputs
            self.digitalLines[ii] = DigitalEntry(jj,daq.lines[jj],self)
            self.digitalLines[ii].setGeometry(QtCore.QRect(self.column*350+20, self.cursor, 300, 20))
            self.digitalLines[ii].setObjectName("digitalLine"+str(ii))
            
            self.digitalLines[ii].valueChanged.connect(lambda channel, value: self.changeDigital(channel,value))
            
            self.cursor += 20
            
        self.cursor += 20 

        for ii in range(daq.network_outputs):
            jj = ii + daq.analog_outputs + daq.digital_outputs
            self.networkLines[ii] = NetworkEntry(jj,daq.lines[jj],self)
            self.networkLines[ii].setGeometry(QtCore.QRect(self.column*350+20, self.cursor, 400, 100))
            self.networkLines[ii].setObjectName("NetworkLine"+str(ii))
                   
            self.networkLines[ii].valueChanged.connect(lambda channel, subchannel, function, value: self.changeNetwork(channel,subchannel,function,value))
            
            self.cursor += 120
            
        self.cursor += 20
        
        self.lbPushBeam = QtWidgets.QLabel(self)
        self.lbPushBeam.setGeometry(QtCore.QRect(self.column*350+20,self.cursor,100,20))
        self.lbPushBeam.setText("Push Beam (ms)")
        self.lbPushBeam.setObjectName("lbPushBeam")
        self.sbPushBeamOn = QtWidgets.QSpinBox(self)
        self.sbPushBeamOn.setGeometry(QtCore.QRect(self.column*350+20+105,self.cursor,55,20))
        self.sbPushBeamOn.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbPushBeamOn.setMinimum(0)
        self.sbPushBeamOn.setMaximum(1000)
        self.sbPushBeamOn.setSingleStep(1)
        self.sbPushBeamOn.setValue(70)
        self.sbPushBeamOn.setObjectName("sbPushBeamOn")
        self.lbPushBeamOn = QtWidgets.QLabel(self)
        self.lbPushBeamOn.setGeometry(QtCore.QRect(self.column*350+20+165,self.cursor,20,20))
        self.lbPushBeamOn.setText("On")
        self.lbPushBeamOn.setObjectName("lbPushBeamOn")
        self.sbPushBeamOff = QtWidgets.QSpinBox(self)
        self.sbPushBeamOff.setGeometry(QtCore.QRect(self.column*350+20+190,self.cursor,55,20))
        self.sbPushBeamOff.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbPushBeamOff.setMinimum(0)
        self.sbPushBeamOff.setMaximum(1000)
        self.sbPushBeamOff.setSingleStep(1)
        self.sbPushBeamOff.setValue(400)
        self.sbPushBeamOff.setObjectName("sbPushBeamOff")
        self.lbPushBeamOff = QtWidgets.QLabel(self)
        self.lbPushBeamOff.setGeometry(QtCore.QRect(self.column*350+20+250,self.cursor,20,20))
        self.lbPushBeamOff.setText("Off")
        self.lbPushBeamOff.setObjectName("lbPushBeamOff")
        self.lbPushBeamValue = QtWidgets.QLabel(self)
        self.lbPushBeamValue.setGeometry(QtCore.QRect(self.column*350+20+275,self.cursor,35,20))
        self.lbPushBeamValue.setText("Ampl:")
        self.lbPushBeamValue.setObjectName("lbPushBeamValue")
        self.sbPushBeamValue = QtWidgets.QSpinBox(self)
        self.sbPushBeamValue.setGeometry(QtCore.QRect(self.column*350+20+315,self.cursor,70,20))
        self.sbPushBeamValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbPushBeamValue.setMinimum(self.amp_min_val)
        self.sbPushBeamValue.setMaximum(self.amp_max_val)
        self.sbPushBeamValue.setSingleStep(self.amp_increment)
        self.sbPushBeamValue.setValue(self.amp_default)        
        self.cbPushBeam = QtWidgets.QCheckBox(self)
        self.cbPushBeam.setGeometry(QtCore.QRect(self.column*350+20+390,self.cursor,60,20))
        self.cbPushBeam.setChecked(False)
        self.cbPushBeam.setText("Cycle")
        self.cbPushBeam.setObjectName("cbPushBeam")
        self.cbCycleMOT1 = QtWidgets.QCheckBox(self)
        self.cbCycleMOT1.setGeometry(QtCore.QRect(self.column*350+20+470,self.cursor,60,20))
        self.cbCycleMOT1.setChecked(False)
        self.cbCycleMOT1.setText("MOT1")
        self.cbCycleMOT1.setObjectName("cbCycleMOT1")
        
        self.tPushBeam = QtCore.QTimer()
        self.pushBeamOn = False
        
        self.cursor += 30
        
        self.lbFreqScan = QtWidgets.QLabel(self)
        self.lbFreqScan.setGeometry(QtCore.QRect(self.column*350+20,self.cursor,100,20))
        self.lbFreqScan.setText("Scan Frequency")
        self.lbFreqScan.setObjectName("lbFreqScan")
        
        self.cbFrequencyScan = QtWidgets.QCheckBox(self)
        self.cbFrequencyScan.setGeometry(QtCore.QRect(self.column*350+130,self.cursor,60,20))
        self.cbFrequencyScan.setChecked(False)
        self.cbFrequencyScan.setText("Scan")
        self.cbFrequencyScan.setObjectName("cbFrequencyScan")
        
        self.tFrequencyScan = QtCore.QTimer()
        self.frequencyScanOn = False
        self.scanRising = True

        self.cursor += 20

        self.lbFSChannel = QtWidgets.QLabel(self)
        self.lbFSChannel.setGeometry(QtCore.QRect(self.column*350+20,self.cursor,60,20))
        self.lbFSChannel.setText("Channel")
        self.lbFSChannel.setObjectName("lbFSChannel")
        self.cbFSChannel = QtWidgets.QComboBox(self)
        self.cbFSChannel.setGeometry(QtCore.QRect(self.column*350+85,self.cursor,80,20))
        
        for ii in range(daq.network_outputs):
            jj = ii + daq.analog_outputs + daq.digital_outputs
            self.cbFSChannel.insertItem(ii,daq.lines[jj].label)
            
        self.lbFSSubChannel = QtWidgets.QLabel(self)
        self.lbFSSubChannel.setGeometry(QtCore.QRect(self.column*350+170,self.cursor,100,20))
        self.lbFSSubChannel.setText("SubChannel")
        self.lbFSSubChannel.setObjectName("lbFSSubChannel")
        self.cbFSSubChannel = QtWidgets.QComboBox(self)
        self.cbFSSubChannel.setGeometry(QtCore.QRect(self.column*350+275,self.cursor,80,20))
        
        for ii in range(channelsPerDDS):
            self.cbFSSubChannel.insertItem(ii,daq.lines[daq.analog_outputs+daq.digital_outputs].labels[ii])
                        
        self.retranslateUi(self)
        self.cbPushBeam.stateChanged.connect(self.pushBeamStateChanged)
        self.tPushBeam.timeout.connect(self.pushBeamTimedOut)
        self.cbFSChannel.currentIndexChanged.connect(self.FSChannelChanged)
        self.cbFrequencyScan.stateChanged.connect(self.frequencyScanStateChanged)
        self.tFrequencyScan.timeout.connect(self.frequencyScanTimedOut)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lbChannel.setText(_translate("Form", "Channel"))
        self.lbValue.setText(_translate("Form", "Value"))
        
    def changeAnalog(self,channel,value):
        daq.writeAnalog(channel,value)
        
    def changeDigital(self,channel,value):
        daq.writeDigital(channel,value)
            
    def changeNetwork(self,channel,subchannel,function,value):
        daq.writeNetwork(channel,subchannel,function,value)
        
    def pushBeamStateChanged(self,state):
        mot1chan = 0
        mot1subchan = 1
        chan = self.pushBeamChannel
        netchan = chan - daq.analog_outputs - daq.digital_outputs
        subchan = self.pushBeamSubChannel
        if state == QtCore.Qt.Checked:
            self.mot1val = self.networkLines[mot1chan].getValue(mot1subchan,1)
            if self.cbCycleMOT1.isChecked():
                self.networkLines[mot1chan].changeValue(mot1subchan,1,0)
            self.pushBeamOn = True
            self.tPushBeam.start(self.sbPushBeamOn.value())
        else:
            if self.cbCycleMOT1.isChecked():
              self.networkLines[mot1chan].changeValue(mot1subchan,1,self.mot1val)
            self.pushBeamOn = False
            self.tPushBeam.stop()
            self.networkLines[netchan].changeValue(subchan,1,0)
            
    def pushBeamTimedOut(self):
        mot1chan = 0
        mot1subchan = 1
        chan = self.pushBeamChannel
        netchan = chan - daq.analog_outputs - daq.digital_outputs
        subchan = self.pushBeamSubChannel
        self.tPushBeam.stop()
        if self.pushBeamOn == True:
            self.networkLines[netchan].changeValue(subchan,1,0)
            if self.cbCycleMOT1.isChecked():
                self.networkLines[mot1chan].changeValue(mot1subchan,1,self.mot1val)
            self.tPushBeam.start(self.sbPushBeamOff.value())
        else:
            self.networkLines[netchan].changeValue(subchan,1,self.sbPushBeamValue.value())
            if self.cbCycleMOT1.isChecked():
                self.networkLines[mot1chan].changeValue(mot1subchan,1,0)
            self.tPushBeam.start(self.sbPushBeamOn.value())
        self.pushBeamOn = not self.pushBeamOn
            
    def FSChannelChanged(self,index):
        for ii in range(channelsPerDDS):
            chan = self.cbFSChannel.currentIndex() + daq.analog_outputs + daq.digital_outputs
            self.cbFSSubChannel.setItemText(ii,daq.lines[chan].labels[ii])
        
    def frequencyScanStateChanged(self,state):
        netchan = self.cbFSChannel.currentIndex()
        chan = netchan + daq.analog_outputs + daq.digital_outputs
        subchan = self.cbFSSubChannel.currentIndex()
        if state == QtCore.Qt.Checked:
            self.frequencyScanOn = True
            self.tFrequencyScan.start(scanTick)
        else:
            self.frequencyScanOn = False
            self.tFrequencyScan.stop()
    
    def frequencyScanTimedOut(self):
        netchan = self.cbFSChannel.currentIndex()
        chan = netchan + daq.analog_outputs + daq.digital_outputs
        subchan = self.cbFSSubChannel.currentIndex()
        
        freq_min_val = daq.lines[chan].freq_min
        freq_max_val = daq.lines[chan].freq_max
        freq_increment = daq.lines[chan].freq_increment
        freq_default = daq.lines[chan].freq_default
        
        current_value = self.networkLines[netchan].getValue(subchan,0)
        
        if current_value == freq_max_val:
            self.scanRising = False
        elif current_value == freq_min_val:
            self.scanRising = True
        else:
            self.scanRising = self.scanRising
        
        if self.scanRising:
            inc = freq_increment
        else:
            inc = -freq_increment
            
        self.networkLines[netchan].changeValue(subchan,0,current_value+inc)
        
        
