#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 09:06:07 2019

@author: lab
"""

from PyQt5 import QtCore, QtGui, QtWidgets

import os
import ctypes
import numpy as np

from datatime import datetime;

import subprocess

from constants import *

# 65536 byte FIFO
# 16 bits per value
# 24 channels
# = 170 samples
#max_samples = 100

class EDRE_Interface(object):
    def __init__(self):
        
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
        else:
            print("Card number " + str(card) + "not found.\n")
            
        return result
        
    def writeChannel(self,card,channel,value):
        
        if card == 0:
            result = self.edrelib.EDRE_DAWrite(self.analog0,channel,value)
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
        else:
           print("Card number " + str(card) + "not found.\n")        
                    
        return result

    def writeBuffer(self,samples,channels,data):
        now = datetime.now()
        filename = now.strftime("%Y%m%d%H%M")
        fullpath = data_file_root+'/'+filename
        try:
            osmkdir(fullpath)
        except FileExistsError:
            print("Directory ",fullpath," already exists)
            
        file = open(fullpath+'/'+filename+".txt","w+")
        for ii in range(samples):
            for jj in range(channels):
                file.write("%ld",data[ii*channels+jj])
                if jj + 1 == channels:
                    file.write("\n")
                else:
                    file.write("\t")
        file.close()
        
        return fullpath, filename

    def run(self,card,filename):
        
        if card == 0:
            result = subprocess.run(["stream",filename])
        else:
            print("Card number " + str(card) + "not found.\n")
                  
        return result     
           
    
if __name__ == "__main__":
    test = EDRE_Interface()

    data = np.ones((4,200000))
    inc = 2*np.pi/512
    
    for ii in range(150000):
        for jj in range(4):
            data[jj][ii] = round(np.sin(ii*inc)*1000000.0)
        
    mybuffer = data.flatten('F')
    
    test.stop(0)
    
    test.run(0,200000,mybuffer)
    
