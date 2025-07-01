# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleSelect.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import *
from Utilities import *

from DAQ import DAQ, daq

class formModuleSelect(QtWidgets.QDialog):
    
    def __init__(self, num_modules, modules, parent = None):
        super(formModuleSelect,self).__init__(parent)
 
        self.num_modules = num_modules
        self.modules = modules
       
        self.parent = parent
        self.ui = parent.ui

        ag_rows = 8
        dl_rows = 4
        nk_rows = 1
        
        self.setObjectName("formModuleSelect")
        self.resize(420, 460)
        
        self.lbName = QtWidgets.QLabel(self)
        self.lbName.setGeometry(QtCore.QRect(10,10,100,20))
        self.lbName.setObjectName("lbName")
        self.leName = QtWidgets.QLineEdit(self)
        self.leName.setGeometry(QtCore.QRect(115,10,100,20))
        self.leName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.leName.setObjectName("leName")
        
        self.bbOkayCancel = QtWidgets.QDialogButtonBox(self)
        self.bbOkayCancel.setGeometry(QtCore.QRect(10, 420, 231, 32))
        self.bbOkayCancel.setOrientation(QtCore.Qt.Horizontal)
        self.bbOkayCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bbOkayCancel.setCenterButtons(True)
        self.bbOkayCancel.setObjectName("bbOkayCancel")

        self.lbStartTime = QtWidgets.QLabel(self)
        self.lbStartTime.setGeometry(QtCore.QRect(10, 40, 100, 20))
        self.lbStartTime.setObjectName("lbStartTime")
        self.sbStartTime = QtWidgets.QSpinBox(self)
        self.sbStartTime.setGeometry(QtCore.QRect(105, 40, 100, 20))
        self.sbStartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbStartTime.setMinimum(0)
        self.sbStartTime.setMaximum(maximumStartTime)
        self.sbStartTime.setSingleStep(timeIncrement)
        self.sbStartTime.setValue(0)
        self.sbStartTime.setObjectName("sbStartTime")
        
        self.lbDuration = QtWidgets.QLabel(self)
        self.lbDuration.setGeometry(QtCore.QRect(210, 40, 95, 20))
        self.lbDuration.setObjectName("lbDuration")
        self.sbDuration = QtWidgets.QSpinBox(self)
        self.sbDuration.setGeometry(QtCore.QRect(310, 40, 100, 20))
        self.sbDuration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbDuration.setMinimum(0)
        self.sbDuration.setMaximum(maximumDuration)
        self.sbDuration.setSingleStep(timeIncrement)
        self.sbDuration.setValue(defaultDuration)
        self.sbDuration.setObjectName("sbDuration")

        self.gbAnalogChannels = QtWidgets.QGroupBox(self)
        self.gbAnalogChannels.setGeometry(QtCore.QRect(10, 70, 300, 181))
        self.gbAnalogChannels.setObjectName("gbAnalogChannels")

        self.cbAnalog = {}

        for ii in range(daq.analog_outputs):
            xx = ii//ag_rows
            yy = ii%ag_rows
            self.cbAnalog[ii] = QtWidgets.QCheckBox(self.gbAnalogChannels)
            self.cbAnalog[ii].setGeometry(QtCore.QRect(xx*90+5, 20*yy+20, 85, 21))
            self.cbAnalog[ii].setObjectName("cbAnalog"+str(ii))

        self.gbDigitalChannels = QtWidgets.QGroupBox(self)
        self.gbDigitalChannels.setGeometry(QtCore.QRect(10, 260, 300, 101))
        self.gbDigitalChannels.setObjectName("gbDigitalChannels")
        
        self.cbDigital = {}
        
        for ii in range(daq.digital_outputs):
            xx = ii//dl_rows
            yy = ii%dl_rows
            self.cbDigital[ii] = QtWidgets.QCheckBox(self.gbDigitalChannels)
            self.cbDigital[ii].setGeometry(QtCore.QRect(xx*90+5, yy*20+20, 85, 21))
            self.cbDigital[ii].setObjectName("cbDigital"+str(ii))
            
        self.gbNetworkChannels = QtWidgets.QGroupBox(self)
        self.gbNetworkChannels.setGeometry(QtCore.QRect(10, 370, 300, 41))
        self.gbNetworkChannels.setObjectName("gbNetworkChannels")

        self.cbNetwork = {}
        
        for ii in range(daq.network_outputs):
            xx = ii//nk_rows
            yy = ii%nk_rows

            self.cbNetwork[ii] = QtWidgets.QCheckBox(self.gbNetworkChannels)
            self.cbNetwork[ii].setGeometry(QtCore.QRect(xx*90+5, yy*20+20, 85, 21))
            self.cbNetwork[ii].setObjectName("cbNetwork"+str(ii))

        self.retranslateUi(self)
        self.bbOkayCancel.accepted.connect(self.addModule)
        self.bbOkayCancel.rejected.connect(self.close)
        self.sbStartTime.valueChanged.connect(self.update)
        self.sbDuration.valueChanged.connect(self.update)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.update()

    def retranslateUi(self, formModuleSelect):
        _translate = QtCore.QCoreApplication.translate
        formModuleSelect.setWindowTitle(_translate("formModuleSelect", "Dialog"))
        self.lbName.setText(_translate("formModuleSelect", "Module Name:"))
        self.lbStartTime.setText(_translate("formModuleSelect", "Start Time (us):"))
        self.lbDuration.setText(_translate("formModuleSelect", "Duration (us):"))
        self.gbAnalogChannels.setTitle(_translate("formModuleSelect", "Analog"))
        for ii in range(daq.analog_outputs):
            self.cbAnalog[ii].setText(_translate("formModuleSelect", daq.lines[ii].label))
        self.gbDigitalChannels.setTitle(_translate("formModuleSelect", "Digital"))
        for ii in range(daq.digital_outputs):
            self.cbDigital[ii].setText(_translate("formModuleSelect", daq.lines[ii+daq.analog_outputs].label))
        self.gbNetworkChannels.setTitle(_translate("formModuleSelect", "Network"))
        for ii in range(daq.network_outputs):
            self.cbNetwork[ii].setText(_translate("formModuleSelect", daq.lines[ii+daq.analog_outputs+daq.digital_outputs].label))


    def addModule(self):
        self.ui.addModule(self)
        self.close()

    def update(self):
        startTime = self.sbStartTime.value()
        duration = self.sbDuration.value()-timeIncrement
        endTime = startTime + duration
        
        for ii in range(self.num_modules):
            mstart = self.modules[ii].sbStartTime.value()
            mddur = self.modules[ii].sbDuration.value()-timeIncrement
            mend = mstart+mddur
            if overlap(startTime,endTime,mstart,mend):
                for jj in range(self.modules[ii].num_analogLines):
                    self.cbAnalog[self.modules[ii].analogLines[jj].getChannelNumber()].setEnabled(False)
                for jj in range(self.modules[ii].num_digitalLines):
                    self.cbDigital[self.modules[ii].digitalLines[jj].getChannelNumber()-daq.analog_outputs].setEnabled(False)
                for jj in range(self.modules[ii].num_networkLines):
                    self.cbNetwork[self.modules[ii].networkLines[jj].getChannelNumber()-daq.analog_outputs-daq.digital_outputs].setEnabled(False)
            else:
                for jj in range(self.modules[ii].num_analogLines):
                    self.cbAnalog[self.modules[ii].analogLines[jj].getChannelNumber()].setEnabled(True)
                for jj in range(self.modules[ii].num_digitalLines):
                    self.cbDigital[self.modules[ii].digitalLines[jj].getChannelNumber()-daq.analog_outputs].setEnabled(True)
                for jj in range(self.modules[ii].num_networkLines):
                    self.cbNetwork[self.modules[ii].networkLines[jj].getChannelNumber()-daq.analog_outputs-daq.digital_outputs].setEnabled(True)
