#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 09:06:07 2019

@author: lab
"""

from PyQt5 import QtCore, QtGui, QtWidgets

import ctypes
import numpy as np
import threading
import sys

from constants import *

# 65536 byte FIFO
# 16 bits per value
# 24 channels
# = 170 samples
#max_samples = 100

class MyGui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()
        self.edre = EDRE_Interface(self)
        self.edre.start()

    def initUi(self):
        self.setGeometry(500,500,300,300)
        self.pb = QtWidgets.QPushButton("Button",self)
        self.pb.move(50,50)
        self.pb.clicked.connect(self.doIt)
        
        
    def doIt(self):
        data = np.ones((chanFIFO,200000),dtype=np.long)
        inc = 2*np.pi/512
    
        for ii in range(150000):
            for jj in range(chanFIFO):
                data[jj][ii] = round(np.sin(ii*inc)*1000000.0*jj)

        self.edre.stopFIFO(0)
        result = self.edre.writeChannel(0,0,1000000)
        print("Result: " + str(result))
        result = self.edre.query(0,7,0)
        print("Result: " + str(result))
        result = self.edre.query(0,202,0)
        print("Result: " + str(result))
        result = self.edre.query(0,205,0)
        print("Result: " + str(result))
   
        self.edre.stopFIFO(0)
    
        self.edre.runFIFO(200000,data)


class EDRE_Interface(QtCore.QThread):
    
#    sig = QtCore.pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
#        super(EDRE_Interface,self).__init__(self, *args, **kwargs)
        
        self.analog0 = 1000034286 

        self.initial = 0
        self.samples = 0
        self.left = 0
        self.values = np.zeros((chanFIFO,1))
        
        self.edrelib = ctypes.cdll.LoadLibrary('/usr/lib/libedreapi.so')
        
    def resetChannels(self,card):
        return 0

    def waitOnInterrupt(self,card):
        if card == 0:
            result = self.edrelib.EDRE_WaitOnInterrupt(self.analog0)
        
        else:
            print("Card number" + str(card) + "not found.\n")

        return result
       
    def query(self,card,queryCode,parameter):
        if card == 0:
            result = self.edrelib.EDRE_Query(self.analog0,queryCode,parameter)
            print("Query result: ",result)
        else:
            print("Card number " + str(card) + "not found.\n")
            
        return result
        
    def writeChannel(self,card,channel,value):
        
        if card == 0:
            result = self.edrelib.EDRE_DAWrite(self.analog0,channel,value)
            print("Write result: ",result)
        else:
           print("Card number " + str(card) + "not found.\n")

        return result
            
    def controlFIFO(self,card,command):
        ''' Command
        0:    NULL
        1:    Start
        2:    Stop
        3:    Pause
        4:    Continue
        '''
        if card == 0:
            result = self.edrelib.EDRE_DAControl(self.analog0,0,command)
            print("Control result: ",result)
        else:
           print("Card number " + str(card) + "not found.\n")        
                    
        return result
    
    def startFIFO(self,card):
        return self.controlFIFO(card,1)
        
    def stopFIFO(self,card):
        return self.controlFIFO(card,2)
     
    def initFIFO(self,card,samples,values):

        if card == 0:
            result = self.edrelib.EDRE_DAConfig(self.analog0,1,freqFIFO,0,1,0,samples,values)
            print("Init result: ",result)
        else:
           print("Card number " + str(card) + "not found.\n")        
                    
        return result
     
    def updateFIFO(self,card,samples,values):

        if card == 0:
            result = self.edrelib.EDRE_DAUpdateData(self.analog0,1,samples,values)
            print("Update result: ",result)
        else:
           print("Card number " + str(card) + "not found.\n")        
                    
        return result     

    def runFIFO(self,samples,values):
        
        self.initial = 0
        self.samples = samples
        self.left = samples
        self.values = values
        
        return self.run()
    
    def run(self):
        
        if self.samples*chanFIFO < largest_chunk_size:
            size = self.samples
        else:
            size = largest_chunk_size//chanFIFO

        self.left -= size

        chunk = np.zeros((chanFIFO,size),dtype=np.long)

        chunk = self.values[:][self.initial:(self.initial+size-1)]
            
        chunk.flatten('F')
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(waitFIFO) # ms
#        self.timer.moveToThread(self)
        self.timer.timeout.connect(lambda: self.loopFIFO())

        self.initFIFO(0,size,chunk.ctypes.data_as(ctypes.POINTER(ctypes.c_long)))

        self.controlFIFO(0,1)

        self.timer.start()
        
        self.exec_()
        
    def uploadData(self):

        space = self.query(0,205,0)
        space/= 2
        
        if space > 0:
            if self.left*chanFIFO < space:
                size = self.left
            else:
                size = space//chanFIFO

            if not size:
                size = 2
                            
            chunk = np.zeros((chanFIFO,size),dtype=np.long)
                
            chunk = self.values[:][self.initial:(self.initial+size-1)]
        
            chunk.flatten('F')
        
            self.updateFIFO(0,size,chunk.ctypes.data_as(ctypes.POINTER(ctypes.c_long)))
        
            self.initial += size
            self.left -= size
    
    def loopFIFO(self):
        
        if self.initial >= self.samples:
            self.timer.stop()
            self.timer.deleteLater()
            self.waitOnInterrupt(0)
            self.controlFIFO(0,2)
            self.resetChannels(0)
            return
        
        self.uploadData()        
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = MyGui()
    gui.show()
    sys.exit(app.exec_())
    

    