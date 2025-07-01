# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleAnalogLine.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from Either import *
from Parsers import *

from DAQ import *

from dataTypes import *
from analogDialog import *
from digitalDialog import *
from networkDialog import *
    
class EventButton(QtWidgets.QPushButton):
    def __init__(self, number, parent = None):
        super(EventButton,self).__init__(parent)
        
        self.number = number
        
        self.parent = parent
        
        self.event = Nothing()
        
    def setEvent(self, event):
        self.event = Just(event)
        
    def getEvent(self):
        return self.event

    def editEvent(self):
        pass
    
class AnalogButton(EventButton):
    def __init__(self, channel, number, parent = None):
        super(AnalogButton,self).__init__(number,parent)
        
        self.channel = channel

    def editEvent(self):
        start = self.parent.getLatestTime(self.number)
        duration = self.parent.getModuleEndTime()-start
        dialog = analogDialog(self.channel,start,duration,self.event,self)
        dialog.show()

class DigitalButton(EventButton):
    def __init__(self, channel, number, parent = None):
        super(DigitalButton,self).__init__(number,parent)
        
        self.channel = channel

    def editEvent(self):
        start = self.parent.getLatestTime(self.number)
        duration = self.parent.getModuleEndTime()-start        
        dialog = digitalDialog(self.channel,start,duration,self.event,self)
        dialog.show()

class NetworkButton(EventButton):
    def __init__(self,channel,number,parent = None):
        super(NetworkButton,self).__init__(number,parent)
        
        self.channel = channel
        
    def editEvent(self):
        start = self.parent.getLatestTime(self.number)
        duration = self.parent.getModuleEndTime()-start        
        dialog = networkDialog(self.channel,start,duration,self.event,self)
        dialog.show()
        
class ModuleLine(QtWidgets.QWidget):
    def __init__(self, channel, startTime, module, parent = None):
        super(ModuleLine,self).__init__(parent)
        
        self.channel = channel
        
        self.startTime = startTime
        self.Module = module
        
        self.parent = parent
        
        self.label = daq.lines[channel].label

        self.pbModuleElements = {}
        self.num_moduleElements = 0
        
        self.left = 60
        self.width = 30

        self.setObjectName("ModuleLine")
        self.resize(self.width, 20)
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(0, 0, self.left, 20))
        self.lbChannel.setObjectName("lbChannel")
        self.pbRemoveLineElement = QtWidgets.QPushButton(self)
        self.pbRemoveLineElement.setGeometry(QtCore.QRect(self.left+80,0,30,20))
        self.pbRemoveLineElement.setObjectName("pbRemoveLineElement")
        self.pbRemoveLineElement.setEnabled(False)
        self.pbAddLineElement = QtWidgets.QPushButton(self)
        self.pbAddLineElement.setGeometry(QtCore.QRect(self.left+110, 0, 30, 20))
        self.pbAddLineElement.setObjectName("pbAddLineElement")
        self.pbModuleElements[self.num_moduleElements] = self.createButton()
        self.pbModuleElements[self.num_moduleElements].setGeometry(QtCore.QRect(self.left, 0, 80, 20))
        self.pbModuleElements[self.num_moduleElements].setObjectName("pbModuleElement"+str(self.num_moduleElements))
        
        self.width += 80
        
        self.retranslateUi(self.parent)
        self.pbModuleElements[self.num_moduleElements].clicked.connect(self.pbModuleElements[self.num_moduleElements].editEvent)
        self.pbRemoveLineElement.clicked.connect(self.removeEvent)
        self.pbAddLineElement.clicked.connect(self.addEvent)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.num_moduleElements += 1
        
    def retranslateUi(self, fModuleAnalogLine):
        _translate = QtCore.QCoreApplication.translate
        fModuleAnalogLine.setWindowTitle(_translate("ModuleLine", "Form"))
        self.lbChannel.setText(_translate("ModuleLine", self.label))
        self.pbModuleElements[0].setText(_translate("ModuleLine", "Details"))
        self.pbRemoveLineElement.setText(_translate("ModuleLine", "-"))
        self.pbAddLineElement.setText(_translate("ModuleLine", "+"))

    def createButton(self):
        return EventButton(self.channel,self.num_moduleElements,self)
        
    def updateChannelNumber(self, channel):
        self.channel = channel
        
    def getChannelNumber(self):
        return self.channel

    def addEvent(self):
        self.pbRemoveLineElement.hide()
        self.pbAddLineElement.hide()
        
        self.pbModuleElements[self.num_moduleElements] = self.createButton()
        self.pbModuleElements[self.num_moduleElements].setText("Details")
        self.pbModuleElements[self.num_moduleElements].setGeometry(QtCore.QRect(self.width, 0, 80, 20))
        self.pbModuleElements[self.num_moduleElements].setObjectName("pbModuleElement"+str(self.num_moduleElements))
        self.pbModuleElements[self.num_moduleElements].show()
        
        self.width += 80
        
        self.pbModuleElements[self.num_moduleElements].clicked.connect(self.pbModuleElements[self.num_moduleElements].editEvent)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.pbRemoveLineElement.setGeometry(QtCore.QRect(self.width,0,30,20))
        self.pbRemoveLineElement.setEnabled(True)
        self.pbRemoveLineElement.show()
        
        self.pbAddLineElement.setGeometry(QtCore.QRect(self.width+30,0,30,20))
        self.pbAddLineElement.show()
       
        self.num_moduleElements += 1

        self.redoLayout()

    def removeEvent(self):
        self.pbRemoveLineElement.hide()
        self.pbAddLineElement.hide()
        
        self.num_moduleElements -= 1
        
        self.pbModuleElements[self.num_moduleElements].hide()
        self.pbModuleElements[self.num_moduleElements].setParent(None)
        del self.pbModuleElements[self.num_moduleElements]
        
        self.width -= 80
        
        self.pbRemoveLineElement.setGeometry(QtCore.QRect(self.width,0,30,20))
        if self.num_moduleElements == 0:
            self.pbRemoveLineElement.setEnabled(False)
        else:
            self.pbRemoveLineElement.setEnabled(True)            
        self.pbRemoveLineElement.show()
        
        self.pbAddLineElement.setGeometry(QtCore.QRect(self.width+30,0,30,20))
        self.pbAddLineElement.show()

        self.redoLayout()

    def redoLayout(self):
        
        self.width = 60
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                value = event.value()
                duration = value.Duration
            else:
                duration = 1000
            width = 100 #duration/5                
            self.pbModuleElements[ii].setGeometry(QtCore.QRect(self.width,0,width,20))
            
            self.width += width
            
        self.pbRemoveLineElement.setGeometry(QtCore.QRect(self.width,0,30,20))
        self.pbAddLineElement.setGeometry(QtCore.QRect(self.width+30,0,30,20))
        
        self.width += 60
        
        g = self.geometry()

        if self.width > g.width():
            self.resize(self.width+45,20)
            self.Module.requestNewWidth()
             
    def getLatestTime(self, number):
        button = self.pbModuleElements[number].getEvent()
        if button.is_just():
            val = button.value()
            return val.startTime
        while number > 0:
            number -= 1
            button = self.pbModuleElements[number].getEvent()
            if button.is_just():
                val = button.value()
                return val.startTime+val.Duration
        return self.startTime

    def getModuleEndTime(self):
        return self.Module.getModuleEndTime()

    def populateEvents(self, events):
        self.pbModuleElements[0].setEvent(events.pop(0))
        while events:
            self.addEvent()
            self.pbModuleElements[self.num_moduleElements-1].setEvent(events.pop(0))
            
        self.redoLayout()
        
    def convertToSequence(self):
        return -1, [], []
    
    def toString(self):
        return []
    
class ModuleAnalogLine(ModuleLine):
    def __init__(self, channel, startTime, module, parent = None):
        super(ModuleAnalogLine,self).__init__(channel,startTime,module,parent)
        
    def createButton(self):
        return AnalogButton(self.channel,self.num_moduleElements,self)
        
    def convertToSequence(self):
        sequence = []
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                value = event.value()
                event_list = value.createList()
                sequence.append(event_list)
        
        return self.getChannelNumber(), sequence, []
    
    def toString(self):
        output = 'A'+' '+str(self.getChannelNumber())
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                output += ' '
                output += event.value().toString()
            
        output += '\n'    
            
        return output 

class ModuleDigitalLine(ModuleLine):
    def __init__(self, channel, startTime, module, parent = None):
        super(ModuleDigitalLine,self).__init__(channel,startTime,module,parent)
        
    def createButton(self):
        return DigitalButton(self.channel,self.num_moduleElements,self)
        
    def convertToSequence(self):
        
        sequence = []
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                value = event.value()
                event_list = value.createList()
                sequence.append(event_list)
                
        number = self.getChannelNumber()
        
        return number, sequence, []
    
    def toString(self):
        output = 'D'+' '+str(self.getChannelNumber())
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                output += ' '
                output += event.value().toString()            
           
        output += '\n'    

        return output  
    
class ModuleNetworkLine(ModuleLine):
    def __init__(self, channel, startTime, module, parent = None):
        super(ModuleNetworkLine,self).__init__(channel,startTime,module,parent)
        
    def createButton(self):
        return NetworkButton(self.channel,self.num_moduleElements,self)
        
    def convertToSequence(self):
        
        sequence = []
        operations = []
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                value = event.value()
                (seq,ops) = value.createList()
                sequence.append(seq)
                operations.append(ops)
                
        return self.getChannelNumber(), sequence, operations
    
        
    def toString(self):
        output = 'N'+' '+str(self.getChannelNumber())
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                output += ' '
                output += event.value().toString()
           
        output += '\n'    
            
        return output
