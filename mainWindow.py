# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np

import socket

from moduleSelect import formModuleSelect
from moduleRemove import formModuleRemove
from module import moduleForm, stringToModule
from DAQ import *
    
from PyQt5.Qt import QColor
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import scipy.io as sio

from constants import *
from dataTypes import *
from Parsers import *
from Utilities import *
from Either import *
from DirectControl import *
from Camera import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        self.MainWindow = MainWindow
        
        self.modules = {}
        self.num_modules = 0
        
        self.sequences = {}
        self.networks = {}
        self.seq_index = 0
        
        self.Waveform = Nothing()
        self.Network = Nothing()
        
        MainWindow.setObjectName("Rb Controller")
        MainWindow.resize(1000, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tbMain = QtWidgets.QTabWidget(self.centralwidget)
        self.tbMain.setGeometry(QtCore.QRect(10, 10, 871, 541))
        self.tbMain.setObjectName("tbMain")
        self.tbMain1 = QtWidgets.QWidget()
        self.tbMain1.setObjectName("tbMain1")
        self.tbMain.addTab(self.tbMain1, "")
        self.loMainTab = QtWidgets.QHBoxLayout(self.centralwidget)
        self.loMainTab.addWidget(self.tbMain)
        self.centralwidget.setLayout(self.loMainTab)
    
        self.tbChannelTab = QtWidgets.QWidget(self.tbMain)
        self.loChannelTab = QtWidgets.QVBoxLayout(self.tbChannelTab)    
#        self.tbChannelTab.setWidgetResizable(True)
        self.tbChannelTab.setObjectName("tbChannelTab")
        self.tbChannelTab.setLayout(self.loChannelTab)
        
        self.tbRunTab = QtWidgets.QWidget(self.tbMain)
        self.loRunTab = QtWidgets.QVBoxLayout(self.tbRunTab)
        self.tbRunTab.setObjectName("tbRunTab")
        self.tbRunTab.setLayout(self.loRunTab)
        
        self.tbDirectControlTab = QtWidgets.QWidget(self.tbMain)
        self.loDirectControlTab = QtWidgets.QVBoxLayout(self.tbDirectControlTab)
        self.tbDirectControlTab.setObjectName("tbDirectControlTab")
        self.tbDirectControlTab.setLayout(self.loDirectControlTab)
        
        self.directControl = DirectControl(self.tbDirectControlTab)
        self.directControl.setObjectName("directControl")

        self.loDirectControlTab.addWidget(self.directControl)
        
        self.saChannels = QtWidgets.QScrollArea(self.tbChannelTab)
        self.saChannels.setWidgetResizable(True)
        self.saChannels.setGeometry(QtCore.QRect(10,10,10,10))
        
        self.fButtons = QtWidgets.QFrame(self.tbChannelTab)
        self.fButtons.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.pbAddModule = QtWidgets.QPushButton(self.fButtons)
        self.pbAddModule.setGeometry(QtCore.QRect(10, 10, 80, 20))
        self.pbAddModule.setObjectName("pbAddModule")
        self.pbRemoveModule = QtWidgets.QPushButton(self.fButtons)
        self.pbRemoveModule.setGeometry(QtCore.QRect(10, 10, 80, 20))
        self.pbRemoveModule.setObjectName("pbAddModule")
        self.pbCreateSequence = QtWidgets.QPushButton(self.fButtons)
        self.pbCreateSequence.setGeometry(QtCore.QRect(10,10,80,20))
        self.pbCreateSequence.setObjectName("pbCreateSequence")
        self.pbSaveModules = QtWidgets.QPushButton(self.fButtons)
        self.pbSaveModules.setGeometry(QtCore.QRect(10,10,80,20))
        self.pbSaveModules.setObjectName("pbSaveModules")
        self.pbLoadModules = QtWidgets.QPushButton(self.fButtons)
        self.pbLoadModules.setGeometry(QtCore.QRect(10,10,80,20))
        self.pbLoadModules.setObjectName("pbLoadModules")
        self.loButtons = QtWidgets.QHBoxLayout(self.fButtons)
        self.loButtons.addWidget(self.pbAddModule)
        self.loButtons.addWidget(self.pbRemoveModule)
        self.loButtons.addWidget(self.pbCreateSequence)
        self.loButtons.addWidget(self.pbSaveModules)
        self.loButtons.addWidget(self.pbLoadModules)
        self.loButtons.addStretch()
        self.fButtons.setLayout(self.loButtons)

        self.hlwChannelsContents = QtWidgets.QWidget()
        self.hlwChannelsContents.setObjectName("hlwChannelsContents")
        self.hloChannelsContents = QtWidgets.QHBoxLayout(self.hlwChannelsContents)
        self.hloChannelsContents.setObjectName("hloChannelsContents")
        self.gloChannelsContents = QtWidgets.QGridLayout()
        self.hloChannelsContents.addLayout(self.gloChannelsContents)
        self.saChannels.setWidget(self.hlwChannelsContents)
        
        self.loChannelTab.addWidget(self.fButtons)
        self.loChannelTab.addWidget(self.saChannels,1)

        self.tbMain.addTab(self.tbChannelTab, "")
        
        self.pbRun = QtWidgets.QPushButton(self.tbRunTab)
        self.pbRun.setGeometry(QtCore.QRect(10,10,80,20))
        self.pbRun.setObjectName("pbRun")
        self.pbReset = QtWidgets.QPushButton(self.tbRunTab)
        self.pbReset.setGeometry(QtCore.QRect(100,10,80,20))
        self.pbReset.setObjectName("pbReset")
        
        self.fPicture = Picture(512,512,100,self.tbRunTab)
#        self.fPicture.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.fPicture.setGeometry(400,50,512,512)
        self.fPicture.setObjectName("fPicture")
#        self.fPicture.loadFile('/home/lab/mydata/Programming/RBController/default.fit')
        
        self.tbMain.addTab(self.tbRunTab, "")
        
        self.tbMain.addTab(self.tbDirectControlTab, "")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 886, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(MainWindow)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tbMain.setCurrentIndex(1)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.save)
        self.actionSaveAs.triggered.connect(self.saveAs)
        self.actionExit.triggered.connect(MainWindow.close)
        self.pbAddModule.clicked.connect(self.createModule)
        self.pbRemoveModule.clicked.connect(self.removeModule)
        self.pbCreateSequence.clicked.connect(self.createSequence)
        self.pbSaveModules.clicked.connect(self.saveModules)
        self.pbLoadModules.clicked.connect(self.loadModules)
        self.pbRun.clicked.connect(self.run)
        self.pbReset.clicked.connect(self.reset)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.openFileName("default.fit")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Rb Controller"))
        self.tbMain.setTabText(self.tbMain.indexOf(self.tbMain1), _translate("MainWindow", "Tab 1"))
        self.pbAddModule.setText(_translate("MainWindow", "Add Module"))
        self.pbRemoveModule.setText(_translate("MainWindow", "Remove Module"))
        self.pbCreateSequence.setText(_translate("MainWindow", "Create Sequence"))
        self.pbSaveModules.setText(_translate("MainWindow", "Save Modules"))
        self.pbLoadModules.setText(_translate("MainWindow", "Load Modules"))
        self.tbMain.setTabText(self.tbMain.indexOf(self.tbChannelTab), _translate("MainWindow", "Channels"))
        self.pbRun.setText(_translate("MainWindow", "Run"))
        self.pbReset.setText(_translate("MainWindow", "Reset"))
        self.tbMain.setTabText(self.tbMain.indexOf(self.tbRunTab), _translate("MainWindow", "Run"))
        self.tbMain.setTabText(self.tbMain.indexOf(self.tbDirectControlTab), _translate("MainWindow", "Direct Control"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "&Open..."))
        self.actionSave.setText(_translate("MainWindow", "&Save as default"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As..."))
        self.actionExit.setText(_translate("MainWindow", "&Exit"))
        
    def createModule(self):
        createModuleDialog = formModuleSelect(self.num_modules,self.modules,self.MainWindow)
        createModuleDialog.show()
        
    def removeModule(self):
        removeModuleDialog = formModuleRemove(self.num_modules,self.MainWindow)
        removeModuleDialog.show()

    def createSequence(self):
        
        commands = {}
        
        self.sequences.clear()
        self.networks.clear()
        
        self.seq_index = 0
        
        start = 0
        finish = 0
        
        layoutGroups = self.orderModules()
        
        for ii in range(len(layoutGroups)):
            item = layoutGroups[ii]
            for jj in range(len(item)):
                module = self.modules[item[jj].index]
                sequences, commands = module.convertToSequences()
                self.sequences[self.seq_index] = sequences
                self.networks[self.seq_index] = commands
                st = module.sbStartTime.value()
                du = module.sbDuration.value()
                if st < start:
                    start = st
                if st + du > finish:
                    finish = st + du
                    
                self.seq_index += 1
        
        length = (finish - start)
        print(length)
        if length % timeIncrement != 0:
            print('Length of sequence is not divisible by ',timeIncrement,'\n')
        
        length = length//timeIncrement
        data = np.zeros((chanFIFO,length))
        print(length)
        for ii in range(chanFIFO):
            line = daq.lines[ii]
            if isinstance(line,AnalogLine):
                data[ii,:] = np.ones((1,length))*line.default
            elif isinstance(line,DigitalLine):
                if line.default:
                    data[ii,:] = np.ones((1,length))*line.on_value
                else:
                    data[ii,:] = np.zeros((1,length))
            else: # Network
                data[ii,:] = np.zeros((1,length))
                
#        print("sequences: ",self.sequences)
        print("networks: ",self.networks)
        
        for ii in range(self.seq_index):
            sequence = self.sequences[ii]

            for jj in sequence.keys():

                channel = jj[1]
                values = sequence[jj]

                for kk in range(len(values)):
                    for ll in range(len(values[kk])):
                        val = values[kk][ll][1]
                        line = daq.lines[channel]
                        if isinstance(line,AnalogLine):
                            val = line.calibration(val)
                        elif isinstance(line,DigitalLine):
                            val = val * line.on_value
                        value = round(val)
                        data[channel][values[kk][ll][0]//timeIncrement] = value

            network = self.networks[ii]
            
            print('network ',network)
            
            for jj in network.keys():
                print('jj ',jj)
                print('commands ',commands)
                print('commands[jj] ',commands[jj])
                flat_list = []
                for sublist in commands[jj]:
                    for item in sublist:
                        flat_list.append(item)
                commands[jj] = flat_list
                commands[jj].insert(0,"LOAD,")
                command = network[jj]
                s = ''
                for kk in range(len(command)-1):
                    s += command[kk]
                    s += ','
                s += command[len(command)-1]
                commands[jj].append(s)
                        
        for ii in commands.keys():
            commands[ii].append(",F")
            
        print('commands ',commands)
        
        data = data.astype('long').flatten('F')

        # 2**16 = 4 * 2**14, the FIFO was being given 16 bit values
        # data *= 4 # THIS IS BAD!
        # when run from direct control the value passed to DAQ gets sent correctly.
        # when running through the FIFO this magic multiplication makes things work.

        self.Waveform = Just((length,data))
        self.Network = Just(commands)
        
    def openFile(self):
        
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self.MainWindow,"Load FITS","","FITS Files (*.fit);;All Files (*)", options=options)
        
        self.openFileName(fileName)
        
    def saveAs(self):

        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow,"Save FITS","","FITS Files (*.fit);;All Files (*)", options=options)
        
        self.saveFileName(fileName)
        
    def save(self):
        
        self.saveFileName('default.fit')
        
    def openFileName(self,fileName):
        
        hdu_list = fits.open(fileName)
        
        hdr = hdu_list[0].header
                
        self.directControl.analogLines[0].changeValue(hdr['ANALOG0'])
        self.directControl.analogLines[1].changeValue(hdr['ANALOG1'])
        self.directControl.analogLines[2].changeValue(hdr['ANALOG2'])
        self.directControl.analogLines[3].changeValue(hdr['ANALOG3'])
        self.directControl.analogLines[4].changeValue(hdr['ANALOG4'])
        self.directControl.analogLines[5].changeValue(hdr['ANALOG5'])
        self.directControl.analogLines[6].changeValue(hdr['ANALOG6'])
        self.directControl.analogLines[7].changeValue(hdr['ANALOG7'])
        self.directControl.analogLines[8].changeValue(hdr['ANALOG8'])
        self.directControl.analogLines[9].changeValue(hdr['ANALOG9'])
        self.directControl.analogLines[10].changeValue(hdr['ANALOG10'])
        self.directControl.analogLines[11].changeValue(hdr['ANALOG11'])
        self.directControl.analogLines[12].changeValue(hdr['ANALOG12'])
        self.directControl.analogLines[13].changeValue(hdr['ANALOG13'])
        self.directControl.analogLines[14].changeValue(hdr['ANALOG14'])
        self.directControl.analogLines[15].changeValue(hdr['ANALOG15'])
        self.directControl.analogLines[16].changeValue(hdr['ANALOG16'])
        self.directControl.analogLines[17].changeValue(hdr['ANALOG17'])
        
        self.directControl.digitalLines[0].changeValue(hdr['DIGITAL0'])
        self.directControl.digitalLines[1].changeValue(hdr['DIGITAL1'])
        self.directControl.digitalLines[2].changeValue(hdr['DIGITAL2'])
        self.directControl.digitalLines[3].changeValue(hdr['DIGITAL3'])
        
        self.directControl.networkLines[0].changeValue(0,0,hdr['NET00F'])
        self.directControl.networkLines[0].changeValue(0,1,hdr['NET00A'])
        self.directControl.networkLines[0].changeValue(1,0,hdr['NET01F'])
        self.directControl.networkLines[0].changeValue(1,1,hdr['NET01A'])
        self.directControl.networkLines[0].changeValue(2,0,hdr['NET02F'])
        self.directControl.networkLines[0].changeValue(2,1,hdr['NET02A'])
        self.directControl.networkLines[0].changeValue(3,0,hdr['NET03F'])
        self.directControl.networkLines[0].changeValue(3,1,hdr['NET04A'])
        self.directControl.networkLines[1].changeValue(0,0,hdr['NET10F'])
        self.directControl.networkLines[1].changeValue(0,1,hdr['NET10A'])
        self.directControl.networkLines[1].changeValue(1,0,hdr['NET11F'])
        self.directControl.networkLines[1].changeValue(1,1,hdr['NET11A'])
        self.directControl.networkLines[1].changeValue(2,0,hdr['NET12F'])
        self.directControl.networkLines[1].changeValue(2,1,hdr['NET12A'])
        self.directControl.networkLines[1].changeValue(3,0,hdr['NET13F'])
        self.directControl.networkLines[1].changeValue(3,1,hdr['NET13A'])
        
        self.directControl.sbPushBeamOn.setValue(hdr['PUSHON'])
        self.directControl.sbPushBeamOff.setValue(hdr['PUSHOFF'])
        self.directControl.sbPushBeamValue.setValue(hdr['PUSHVAL'])
        
        data = hdu_list[0].data
        
        self.fPicture.loadData(data)
        
        hdu_list.close()
        
    def saveFileName(self,fileName):
        
        hdr = fits.Header()
        
        hdr['ANALOG0'] = self.directControl.analogLines[0].getValue()
        hdr['ANALOG1'] = self.directControl.analogLines[1].getValue()
        hdr['ANALOG2'] = self.directControl.analogLines[2].getValue()
        hdr['ANALOG3'] = self.directControl.analogLines[3].getValue()
        hdr['ANALOG4'] = self.directControl.analogLines[4].getValue()
        hdr['ANALOG5'] = self.directControl.analogLines[5].getValue()
        hdr['ANALOG6'] = self.directControl.analogLines[6].getValue()
        hdr['ANALOG7'] = self.directControl.analogLines[7].getValue()
        hdr['ANALOG8'] = self.directControl.analogLines[8].getValue()
        hdr['ANALOG9'] = self.directControl.analogLines[9].getValue()
        hdr['ANALOG10'] = self.directControl.analogLines[10].getValue()
        hdr['ANALOG11'] = self.directControl.analogLines[11].getValue()
        hdr['ANALOG12'] = self.directControl.analogLines[12].getValue()
        hdr['ANALOG13'] = self.directControl.analogLines[13].getValue()
        hdr['ANALOG14'] = self.directControl.analogLines[14].getValue()
        hdr['ANALOG15'] = self.directControl.analogLines[15].getValue()
        hdr['ANALOG16'] = self.directControl.analogLines[16].getValue()
        hdr['ANALOG17'] = self.directControl.analogLines[17].getValue()
        
        hdr['DIGITAL0'] = self.directControl.digitalLines[0].getValue()
        hdr['DIGITAL1'] = self.directControl.digitalLines[1].getValue()
        hdr['DIGITAL2'] = self.directControl.digitalLines[2].getValue()
        hdr['DIGITAL3'] = self.directControl.digitalLines[3].getValue()
        
        hdr['NET00F'] = self.directControl.networkLines[0].getValue(0,0)
        hdr['NET00A'] = self.directControl.networkLines[0].getValue(0,1)
        hdr['NET01F'] = self.directControl.networkLines[0].getValue(1,0)
        hdr['NET01A'] = self.directControl.networkLines[0].getValue(1,1)
        hdr['NET02F'] = self.directControl.networkLines[0].getValue(2,0)
        hdr['NET02A'] = self.directControl.networkLines[0].getValue(2,1)
        hdr['NET03F'] = self.directControl.networkLines[0].getValue(3,0)
        hdr['NET04A'] = self.directControl.networkLines[0].getValue(3,1)
        hdr['NET10F'] = self.directControl.networkLines[1].getValue(0,0)
        hdr['NET10A'] = self.directControl.networkLines[1].getValue(0,1)
        hdr['NET11F'] = self.directControl.networkLines[1].getValue(1,0)
        hdr['NET11A'] = self.directControl.networkLines[1].getValue(1,1)
        hdr['NET12F'] = self.directControl.networkLines[1].getValue(2,0)
        hdr['NET12A'] = self.directControl.networkLines[1].getValue(2,1)
        hdr['NET13F'] = self.directControl.networkLines[1].getValue(3,0)
        hdr['NET13A'] = self.directControl.networkLines[1].getValue(3,1)
        
        hdr['PUSHON'] = self.directControl.sbPushBeamOn.value()
        hdr['PUSHOFF'] = self.directControl.sbPushBeamOff.value()
        hdr['PUSHVAL'] = self.directControl.sbPushBeamValue.value()
        
        data = np.zeros((3,512,512))
        
        data[0] = self.fPicture.data
        data[1] = self.fPicture.noAtoms
        data[2] = self.fPicture.noLaser
        
        primary_hdu = fits.PrimaryHDU(data,header=hdr)
        
        hdul = fits.HDUList([primary_hdu])
        hdul.writeto(fileName,overwrite=True)
        
    def saveModules(self):
        
        output = self.toString()
        
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow,"Save Modules","","Module Files (*.rbm);;All Files (*)", options=options)
        
        outputFile = open(fileName,"w")
        outputFile.write(output)
        outputFile.close()
        
    def loadModules(self):
        
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self.MainWindow,"Load Modules","","Module Files (*.rbm);;All Files (*)", options=options)
        
        inputFile = open(fileName,"r")
        data = inputFile.read()
        inputFile.close()

        try:
            
            while len(data) > 0:
            
                data = eatWhiteSpace(data)
            
                self.modules[self.num_modules] = moduleForm(self.num_modules,self,self.hlwChannelsContents)
                data = stringToModule(data,self.modules[self.num_modules])
                self.modules[self.num_modules].show()
            
                self.gloChannelsContents.addWidget(self.modules[self.num_modules])
      
                self.num_modules += 1
        
            self.doLayout()

        except:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Could not load file')
        
    def run(self):
        
        if self.Network.is_just():
            commands = self.Network.value()
            
            for ii in commands.keys():
                command = commands[ii]
                
                address = daq.lines[ii].address
                port = daq.lines[ii].port
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((address, port))
                
                print(command)
                
                array = command.toLatin1()
                buffer = array.data()
                s.send(buffer)
                s.recv(5)
                s.close()   
        
        if self.Waveform.is_just():
            (samples,data) = self.Waveform.value()
#            camera.setTriggers(3,'temp.fit')
            daq.run(samples,data)
#            fits = camera.getImage()
        else:
            print("No waveform to send.")

    def reset(self):
        daq.stop()
        
#    def focus(self):
#        
#        if self.Focusing == False:
#            self.tFocusing.start(100)
#        else:
#            self.tFocusing.stop()
#        self.Focusing = not self.Focusing
            
#    def focusTimedOut(self):
#        fits = camera.shoot(3,'focus.fit')
#        self.fPicture.display(fits)
        
    def addModule(self, formModuleSelect):
        self.modules[self.num_modules] = moduleForm(self.num_modules,self,self.hlwChannelsContents)
        self.modules[self.num_modules].leName.setText(formModuleSelect.leName.text())
        self.modules[self.num_modules].sbStartTime.setValue(formModuleSelect.sbStartTime.value())
        self.modules[self.num_modules].sbDuration.setValue(formModuleSelect.sbDuration.value())

        for ii in range(daq.analog_outputs):
            if formModuleSelect.cbAnalog[ii].isChecked():
                self.modules[self.num_modules].addAnalogLine(ii)
                
        for ii in range(daq.digital_outputs):
            if formModuleSelect.cbDigital[ii].isChecked():
                self.modules[self.num_modules].addDigitalLine(ii+daq.analog_outputs)
                
        for ii in range(daq.network_outputs):
            if formModuleSelect.cbNetwork[ii].isChecked():
                self.modules[self.num_modules].addNetworkLine(ii+daq.analog_outputs+daq.digital_outputs)

#        self.modules[self.num_modules].reSize()

        self.gloChannelsContents.addWidget(self.modules[self.num_modules])

#        self.modules[self.num_modules].show()
        
        self.num_modules += 1
       
        self.doLayout()
        
    def deleteModule(self,moduleNumber):
        
        index = self.num_modules
        
        for ii in range(self.num_modules):
            if self.modules[ii].moduleNumber == ii:
                index = ii
        
        self.modules[index].hide()
        self.gloChannelsContents.removeWidget(self.modules[index])

        for i in range(index,self.num_modules):
            self.modules[i].setModuleNumber(i-1)
        del self.modules[index]
        
        self.num_modules -= 1
        
    def orderModules(self):
        
        moduleLayouts = []
        
        for ii in range(self.num_modules):
            start = self.modules[ii].sbStartTime.value()
            finish = start+self.modules[ii].sbDuration.value()-timeIncrement
            
            moduleLayout = ModuleLayout(ii,ii,start,finish,self.modules[ii].width,self.modules[ii].height)
            
            moduleLayouts.append(moduleLayout)
          
#        moduleLayouts.sort(key=lambda ml:ml.startTime)

        moduleLayouts.sort(key = attrgetter('startTime','finishTime'))

        for ii in range(self.num_modules):
            self.modules[moduleLayouts[ii].index].setModuleNumber(ii)
            moduleLayouts[ii].position = ii
            
        layoutGroups = groupModules(moduleLayouts)
        
        return layoutGroups
        
    def doLayout(self):
        
        for ii in range(self.num_modules):
            self.modules[ii].hide()
            self.gloChannelsContents.removeWidget(self.modules[ii])
            
        layoutGroups = self.orderModules()
        
        print("layoutGroups: ",layoutGroups)

        layoutIntervals = {}
      
        for ii in range(len(layoutGroups)):
            layoutIntervals[ii] = joinIntervalsGroup(layoutGroups[ii])

            start_y = 0
        
            modules = {}
            module_index = 0
            
            layint = layoutIntervals[ii]

            print("layoutIntervals: ",layint)

            modules[module_index] = []

            while layint:
                interval = layint.pop(0)
                if interval[0] == module_index:
                    modules[module_index].append(interval)
                else:
                    module_index += 1
                    modules[module_index] = [interval]

            for jj in range(module_index+1):
                if not modules[jj]:
                    del modules[jj]
            
            for jj in modules.keys():
                print("modules: ",modules)
                start = modules[jj][0][1] 
                finish = modules[jj][0][2]
                
                for kk in range(1,len(modules[jj])):
                    
                    finish = modules[jj][kk][2]

                width = finish - start
                height = self.modules[modules[jj][0][0]].height

                self.gloChannelsContents.addWidget(self.modules[modules[jj][0][0]],start_y//10,start//10,height//10,width//10)
                self.modules[modules[jj][0][0]].show()
                
                start_y += height

    def toString(self):
        
        output = ''
        
        layoutGroups = self.orderModules()
        
        for ii in range(len(layoutGroups)):
            group = layoutGroups[ii]
            for jj in group:
                output += self.modules[jj.index].toString()
                output += '\n'
                
        return output
