# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'module.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from moduleDivider import *

from moduleLine import *

from dataTypes import *

class moduleForm(QtWidgets.QWidget):
           
    def __init__(self, moduleNumber, mainWindow, parent = None):
        super(moduleForm,self).__init__(parent)
        
        self.moduleNumber = moduleNumber
        
        self.mainWindow = mainWindow
        self.parent = parent
        
        self.minWidth = 400
        
        self.width = self.minWidth
        self.height = 300
        
        self.analogLines = {}
        self.num_analogLines = 0
        
        self.digitalLines = {}
        self.num_digitalLines = 0
        
        self.networkLines = {}
        self.num_networkLines = 0
        
        self.headerHeight = 50

        self.cursor = self.headerHeight
                
        self.setObjectName("moduleForm")
        self.resize(self.width, self.height)
        self.setGeometry(QtCore.QRect(0, 0, self.width, self.height))
        
        self.fModule = QtWidgets.QFrame(self)
        self.fModule.resize(self.width,self.height)
        self.fModule.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fModule.setFrameShadow(QtWidgets.QFrame.Raised)
#        self.setWidgetResizable(False)

        self.lbModuleNumber = QtWidgets.QLabel(self.fModule)
        self.lbModuleNumber.setGeometry(QtCore.QRect(5,5,100,20))
        self.lbModuleNumber.setObjectName("lbModuleNumber")

        self.lbName = QtWidgets.QLabel(self)
        self.lbName.setGeometry(QtCore.QRect(110,5,100,20))
        self.lbName.setObjectName("lbName")
        self.leName = QtWidgets.QLineEdit(self)
        self.leName.setGeometry(QtCore.QRect(230,5,100,20))
        self.leName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.leName.setObjectName("leName")
        
        self.lbStartTime = QtWidgets.QLabel(self.fModule)
        self.lbStartTime.setGeometry(QtCore.QRect(5, 25, 100, 20))
        self.lbStartTime.setObjectName("lbStartTime")
        self.sbStartTime = QtWidgets.QSpinBox(self.fModule)
        self.sbStartTime.setGeometry(QtCore.QRect(110, 25,80, 20))
        self.sbStartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbStartTime.setMinimum(0)
        self.sbStartTime.setMaximum(maximumStartTime)
        self.sbStartTime.setSingleStep(timeIncrement)
        self.sbStartTime.setValue(0)
        self.sbStartTime.setObjectName("sbStartTime")
        self.lbDuration = QtWidgets.QLabel(self.fModule)
        self.lbDuration.setGeometry(QtCore.QRect(200, 25, 90, 20))
        self.lbDuration.setObjectName("lbDuration")
        self.sbDuration = QtWidgets.QSpinBox(self.fModule)
        self.sbDuration.setGeometry(QtCore.QRect(300, 25, 90, 20))
        self.sbDuration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbDuration.setMinimum(0)
        self.sbDuration.setMaximum(maximumDuration)
        self.sbDuration.setSingleStep(timeIncrement)
        self.sbDuration.setValue(defaultDuration)
        self.sbDuration.setObjectName("sbDuration")
        
        self.aLine = fmDivider(self.fModule)
        self.aLine.setGeometry(QtCore.QRect(5, self.headerHeight, self.width-10, 20))
        self.aLine.setText("Analog")
        self.aLine.setObjectName("lAnalog")
        
        self.dLine = fmDivider(self.fModule)
        self.dLine.setGeometry(QtCore.QRect(5, self.headerHeight+20, self.width-10, 20))
        self.dLine.setText("Digital")
        self.dLine.setObjectName("lDigital")

        self.nLine = fmDivider(self.fModule)
        self.nLine.setGeometry(QtCore.QRect(5, self.headerHeight+40, self.width-10, 20))
        self.nLine.setText("Network")
        self.nLine.setObjectName("lNetwork")

        self.loModule = QtWidgets.QVBoxLayout()
        self.loModule.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        
        self.loModule.addWidget(self.fModule)

        self.setMinimumSize(self.width,self.height)
        self.setMaximumSize(self.width,self.height)

        self.retranslateUi(self.parent)

#        self.sbStartTime.valueChanged.connect(self.mainWindow.doLayout)
#        self.sbDuration.valueChanged.connect(self.mainWindow.doLayout)
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def retranslateUi(self, moduleForm):
        _translate = QtCore.QCoreApplication.translate
#        moduleForm.setWindowTitle(_translate("moduleForm", "Form"))
        self.lbModuleNumber.setText(_translate("moduleForm", "Module: "+str(self.moduleNumber)))
        self.lbName.setText(_translate("moduleForm", "ModuleName:"))
        self.leName.setText(_translate("moduleForm", ""))
        self.lbStartTime.setText(_translate("moduleForm", "Start Time (us):"))
        self.lbDuration.setText(_translate("moduleForm", "Duration (us):"))

    def setModuleNumber(self,i):
        self.moduleNumber = i
        self.lbModuleNumber.setText("Module: "+str(self.moduleNumber))
        
    def addAnalog(self):
        self.fAnalog = QtWidgets.QFrame(self)
        self.fAnalog.setGeometry(QtCore.QRect(5, self.headerHeight+20, self.width-10, 5))
        self.fAnalog.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fAnalog.setObjectName("fAnalog")
        self.fAnalog.show()
        
    def addDigital(self):
        self.fDigital = QtWidgets.QFrame(self.fModule)
        self.fDigital.setGeometry(QtCore.QRect(5, self.headerHeight+40+20*(self.num_analogLines), self.width-10, 5))
        self.fDigital.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fDigital.setObjectName("fDigital")        

    def addNetwork(self):
        self.fNetwork = QtWidgets.QFrame(self.fModule)
        self.fNetwork.setGeometry(QtCore.QRect(5, self.headerHeight+60+20*(self.num_analogLines+self.num_digitalLines), self.width-10, 5))
        self.fNetwork.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fNetwork.setObjectName("fNetwork")
        
    def addAnalogLine(self, channel,events=None):
        if self.num_analogLines == 0:
            self.addAnalog()
            
        analogg = self.fAnalog.geometry()

        self.cursor = 20*self.num_analogLines

        self.fAnalog.setGeometry(QtCore.QRect(analogg.left(),analogg.top(),analogg.width(),self.cursor+20))

        startTime = self.sbStartTime.value()
        
        self.analogLines[self.num_analogLines] = ModuleAnalogLine(channel,startTime,self,self.fAnalog)
        self.analogLines[self.num_analogLines].setGeometry(5,self.cursor,300,20)
        self.analogLines[self.num_analogLines].updateChannelNumber(channel)
        if events:
            self.analogLines[self.num_analogLines].populateEvents(events)
        self.analogLines[self.num_analogLines].show()
        
        self.num_analogLines += 1
        
        dLineg = self.dLine.geometry()
        self.dLine.setGeometry(QtCore.QRect(dLineg.left(),analogg.top()+self.cursor+20,dLineg.width(),20))
        nLineg = self.nLine.geometry()
        self.nLine.setGeometry(QtCore.QRect(nLineg.left(),analogg.top()+self.cursor+40,nLineg.width(),20))

        self.requestNewWidth()
        self.reSize()

    def addDigitalLine(self,channel,events=None):
        
        if self.num_digitalLines == 0:
            self.addDigital()
            
        digitalg = self.fDigital.geometry()
        
        self.cursor = 20*self.num_digitalLines
        
        self.fDigital.setGeometry(QtCore.QRect(digitalg.left(),digitalg.top(),digitalg.width(),self.cursor+20))

        startTime = self.sbStartTime.value()

        self.digitalLines[self.num_digitalLines] = ModuleDigitalLine(channel,startTime,self,self.fDigital)
        self.digitalLines[self.num_digitalLines].setGeometry(5,self.cursor,300,20)
        self.digitalLines[self.num_digitalLines].updateChannelNumber(channel)
        if events:
            self.digitalLines[self.num_digitalLines].populateEvents(events)
        self.digitalLines[self.num_digitalLines].show()
        
        self.num_digitalLines += 1

        nLineg = self.nLine.geometry()
        self.nLine.setGeometry(QtCore.QRect(nLineg.left(),digitalg.top()+self.cursor+20,nLineg.width(),20))
       
        self.requestNewWidth()
        self.reSize()
        
    def addNetworkLine(self,channel,events=None):
        
        if self.num_networkLines == 0:
            self.addNetwork()
            
        networkg = self.fNetwork.geometry()
        
        self.cursor = 20*self.num_networkLines
        
        self.fNetwork.setGeometry(QtCore.QRect(networkg.left(),networkg.top(),networkg.width(),self.cursor+20))

        startTime = self.sbStartTime.value()

        self.networkLines[self.num_networkLines] = ModuleNetworkLine(channel,startTime,self,self.fNetwork)
        self.networkLines[self.num_networkLines].setGeometry(5,self.cursor,300,20)
        self.networkLines[self.num_networkLines].updateChannelNumber(channel)
        if events:
            self.networkLines[self.num_networkLines].populateEvents(events)
        self.networkLines[self.num_networkLines].show()
        
        self.num_networkLines += 1

        self.requestNewWidth()
        self.reSize()

    def requestNewWidth(self):
        max_width = 0
        for ii in range(self.num_analogLines):
            width = self.analogLines[ii].geometry().width()
            if width > max_width:
                max_width = width
        for ii in range(self.num_digitalLines):
            width = self.digitalLines[ii].geometry().width()
            if width > max_width:
                max_width = width               
        for ii in range(self.num_networkLines):
            width = self.networkLines[ii].geometry().width()
            if width > max_width:
                max_width = width 
                
        if max_width < self.minWidth:
            self.width = self.minWidth
        else:
            self.width = max_width
            
        self.reSize()

    def reSize(self):
        self.height = self.headerHeight+60+20*(self.num_analogLines+self.num_digitalLines+self.num_networkLines)+15
        super(moduleForm,self).resize(self.width,self.height)
        self.fModule.resize(self.width,self.height)
        self.aLine.resize(self.width-10,self.aLine.geometry().height())
        if self.num_analogLines > 0:
            self.fAnalog.resize(self.width,self.fAnalog.geometry().height())
        self.dLine.resize(self.width-10,self.dLine.geometry().height())
        if self.num_digitalLines > 0:
            self.fDigital.resize(self.width,self.fDigital.geometry().height())        
        self.nLine.resize(self.width-10,self.nLine.geometry().height())
        if self.num_networkLines > 0:
            self.fNetwork.resize(self.width,self.fNetwork.geometry().height())  
            
        self.setMinimumSize(self.width,self.height)
        self.setMaximumSize(self.width,self.height)

    def populateModule(self,name,start,duration,analogs,digitals,networks):
        self.leName.setText(name)
        self.sbStartTime.setValue(start)
        self.sbDuration.setValue(duration)
        
        for ii in analogs.keys():
            self.addAnalogLine(ii,analogs[ii])
            
        for ii in digitals.keys():
            self.addDigitalLine(ii,digitals[ii])
            
        for ii in networks.keys():
            self.addNetworkLine(ii,networks[ii])
        
    def getModuleEndTime(self):
        return self.sbStartTime.value()+self.sbDuration.value()
    
    def convertToSequences(self):

        sequences = {}
        operations = {}
        
        for ii in range(self.num_analogLines):
            line = self.analogLines[ii]
            
            number, sequence, _ = line.convertToSequence()
            
            sequences[('A',number)] = sequence
            
        for ii in range(self.num_digitalLines):
            line = self.digitalLines[ii]
            
            number, sequence, _  = line.convertToSequence()
            
            sequences[('D',number)] = sequence
            
        for ii in range(self.num_networkLines):
            line = self.networkLines[ii]
            
            number, sequence, commands = line.convertToSequence()
            
            sequences[('N',number)] = sequence
            operations[number] = commands
            
        return sequences, operations

    def toString(self):
        
        output = 'Name: '
        output += self.leName.text()
        output += '\n'
        output += 'Start time: '
        output += str(self.sbStartTime.value())
        output += '\n'
        output += 'Duration: '
        output += str(self.sbDuration.value())
        output += '\n'
        
        for ii in range(self.num_analogLines):
           output += self.analogLines[ii].toString()
        
        for ii in range(self.num_digitalLines):

           output += self.digitalLines[ii].toString()
                            
        for ii in range(self.num_networkLines):
           output += self.networkLines[ii].toString()
               
        return output
               
