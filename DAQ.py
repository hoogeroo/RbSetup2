#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 09:06:07 2019

@author: lab
"""

from PyQt6 import QtCore, QtGui, QtWidgets

import ctypes
import socket
import numpy as np

from constants import *

# 65536 byte FIFO
# 16 bits per value
# 24 channels
# = 170 samples
#max_samples = 100

from Either import *

class EDRE_Interface(object):
    def __init__(self):
        try:
          self.fifo = ctypes.cdll.LoadLibrary('/home/lab/mydata/Programming/RbController/fifo.so')
        except:
          self.fifo = self.fakefifo()
        print(self.fifo)
        
    def query(self,card,queryCode,parameter):
        result = self.fifo.query(card,queryCode,parameter)
            
        return result
        
    def writeChannel(self,card,channel,value):
        result = self.fifo.writeChannel(card,channel,value)

        return result
            
    def start(self,card):
        result = self.fifo.start(card)
                   
        return result
     
    def stop(self,card):
        result = self.fifo.stop(card)
                   
        return result

    def run(self,card,samples,data):
        result = self.fifo.run(card,samples,data.ctypes.data_as(ctypes.POINTER(ctypes.c_long)))
                  
        return result
    class fakefifo(object):
        def __init__(self):
            print("Doing Fake FIFO")
            
    
class Line():
    def __init__(self,line,label):
        self.line = line
        self.label = label
        
class AnalogLine(Line):
    def __init__(self,line,label,min_val,max_val,increment,default,units,calibration):
        super(AnalogLine,self).__init__(line,label)
        self.min_val = min_val
        self.max_val = max_val
        self.increment = increment
        self.default = default
        self.units = units
        self.calibration = calibration
        
class DigitalLine(Line):
    def __init__(self,line,label,off_value,on_value,default):
        super(DigitalLine,self).__init__(line,label)
        self.off_value = off_value
        self.on_value = on_value
        self.default = default
        
class NetworkLine(Line):
    def __init__(self,line,label,chan0,chan1,chan2,chan3,address,port,freq_min,freq_max,freq_increment,freq_default,amp_min,amp_max,amp_increment,amp_default):
        super(NetworkLine,self).__init__(line,label)
        self.labels = {}
        self.labels[0] = chan0
        self.labels[1] = chan1
        self.labels[2] = chan2
        self.labels[3] = chan3
        self.address = address
        self.port = port
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.freq_increment = freq_increment
        self.freq_default = freq_default
        self.amp_min = amp_min
        self.amp_max = amp_max
        self.amp_increment = amp_increment
        self.amp_default = amp_default

#def calibrate3(input): #HH y-coil calibration
#     610mV = 0.07625A
#     1.23V = 0.15A
#     1.86V = 0.23A
#     2.49 = 0.311A
#    return 7*input
  
#def calibrate4(input): #HH y-coils calibration
#    #340mV = 0.0155A
#    #720mV = 0.0327A
#    #1.1V = 0.05A
#    #1.48V = 0.0673A
#    return 29*input
 
#def calibrate5(input): #HH z-coils calibration
#    #300mV = 0.0127A
#    #640mV = 0.0271A
#    #970mV = 0.0411A
#    #1.31V = 0.0555A
#    return 35*input
 
def calibrate6(input): # anti-HH calibration
    # 400 mV = 8.8
    # 200 mV = 4.8 A
    # 100 mV = 2.8 A
    # 50 mV = 1.8 A
    # 0 mV = 0.8 A
    return 50000*input - 40000

    
class DAQ():
    def __init__(self):

        self.EDRE = EDRE_Interface()
        
        self.analog_outputs = 18
        self.digital_outputs = 4
        self.network_outputs = 2
        
        self.lines = {}
        
        self.lines[0] = AnalogLine(0,"Analog 0",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[1] = AnalogLine(1,"Analog 1",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[2] = AnalogLine(2,"Analog 2",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[3] = AnalogLine(3,"HH 2 X",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[4] = AnalogLine(4,"HH 2 Y",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[5] = AnalogLine(5,"HH 2 Z",-10000,10000,100,0,"mV",lambda x: x*1000)
#        self.lines[6] = AnalogLine(6,"aHH 2",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[6] = AnalogLine(6,"aHH 2",0,100,1,0,"A",calibrate6)
        self.lines[7] = AnalogLine(7,"Analog 7",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[8] = AnalogLine(8,"Analog 8",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[9] = AnalogLine(9,"Analog 9",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[10] = AnalogLine(10,"Analog 10",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[11] = AnalogLine(11,"Analog 11",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[12] = AnalogLine(12,"Analog 12",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[13] = AnalogLine(13,"Analog 13",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[14] = AnalogLine(14,"Analog 14",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[15] = AnalogLine(15,"Analog 15",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[16] = AnalogLine(16,"Analog 16",-10000,10000,100,0,"mV",lambda x: x*1000)
        self.lines[17] = AnalogLine(17,"Analog 17",-10000,10000,100,0,"mV",lambda x: x*1000)
        
        self.lines[18] = DigitalLine(18,"Digital 0",0,5000000,False)
        self.lines[19] = DigitalLine(19,"Digital 1",0,5000000,False)
        self.lines[20] = DigitalLine(20,"Digital 2",0,5000000,False)
        self.lines[21] = DigitalLine(21,"Digital 3",0,5000000,False)
        
        self.lines[22] = NetworkLine(22,"DDS 2","Repump","MOT 1","MOT 2","Push Beam",DDS_2_IP,DDS_2_port,60000,100000,1000,80000,0,1000,100,1000)
        self.lines[23] = NetworkLine(23,"DDS 3","Probe","Unused","Unused","Unused",DDS_3_IP,DDS_3_port,60000,100000,1000,80000,0,1000,100,1000)

    def query(self,queryCode,parameter):
        return self.EDRE.query(0,queryCode,parameter)
            
    def start(self):
        return self.EDRE.start(0)

    def stop(self):
        return self.EDRE.stop(0)

    def run(self,samples,data):
        return self.EDRE.run(0,samples,data)
        
    def writeAnalog(self,channel,value):
        if channel < self.analog_outputs:
            line = self.lines[channel]
            if value < line.min_val:
                val = line.min_val
            elif value > line.max_val:
                val = line.max_val
            else:
                val = value
            result = self.EDRE.writeChannel(0,channel,line.calibration(val))
        else:
            print("Not an analog channel")
            
    def writeDigital(self,channel,value):
        if channel >= self.analog_outputs and channel < (self.analog_outputs+self.digital_outputs):
            line = self.lines[channel]
            if value:
                val = line.on_value
            else:
                val = line.off_value
            self.EDRE.writeChannel(0,channel,val)
        else:
            print("Not a digital channel")
            
    def writeNetwork(self,channel,subchannel,function,value):
#        pass
        if channel >= (self.analog_outputs+self.digital_outputs) and channel < (self.analog_outputs+self.digital_outputs+self.network_outputs):
            line = self.lines[channel]
            if function: # Amplitude
                if value < line.amp_min:
                    val = line.amp_min
                elif value > line.amp_max:
                    val = line.amp_max
                else:
                    val = value
                val = val/1000.0
                ml = '%s,%d,%f' % ('AMPL',subchannel,val)
            else: # Frequency
                if value < line.freq_min:
                    val = line.freq_min
                elif value > line.freq_max:
                    val = line.freq_max
                else:
                    val = value
                val = val/1000.0
                ml = '%s,%d,%f' % ('FREQ',subchannel,val)
            try:
                #print(line.address, line.port) 
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((line.address, line.port))
                s.send(ml.encode())
                s.recv(5)
                s.close()  
            except:
                print('Connection to ',line.address,' refused')          
        else:
            print("Not a network channel")


    def getChannelNumber(self,label):
        
        for ii in range(self.analog_outputs+self.digital_outputs+self.network_outputs):
            line = self.lines[ii]
            if line.label == label:
                return Just(ii), Nothing()
            elif isinstance(line,NetworkLine):
                labels = line.labels
                for jj in range(channelsPerDDS):
                    if labels[jj] == label:
                        return Just(ii), Just(jj)
        return Nothing(), Nothing()
                
     
#daq = DAQ()           
    

    
