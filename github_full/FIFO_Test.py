#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 09:44:43 2019

@author: lab
"""

import ctypes
import numpy as np

from constants import *




class FIFO(object):
    def __init__(self):
        
        self.analog0 = 1000034286 
        self.digital0 = 1000034495     

        self.start = 0

        self.edrelib = ctypes.cdll.LoadLibrary('/usr/lib/libedreapi.so')
        
    def query(self,queryCode,parameter):
        result = self.edrelib.EDRE_Query(self.analog0,queryCode,parameter)
        print("Query result of ",queryCode," : ",result)
            
        return result

    def write(self,channel,value):
        result = self.edrelib.EDRE_DAWrite(self.analog0,channel,value)
  
        if not result:
            print("Write to channel failed.")
  
        return result

    def doStart(self,samples,buffer_p):
        
        chan = 1
        freq = 1000 #freqFIFO
    
        result = self.edrelib.EDRE_DAConfig(self.analog0,chan,freq,0,1,1,4*samples+4,buffer_p) #ctypes.byref(buffer))
        
        st = (ctypes.c_char*256)()
        self.edrelib.EDRE_StrError(result,ctypes.byref(st))
        print(st.value)
        
        if result:
            print("Configuration failed.")
            return result
        
        # DACCOMMANDS
        DA_COMMAND_START = 1
        DA_COMMAND_STOP = 2
        
        result = self.edrelib.EDRE_DAControl(self.analog0,0,DA_COMMAND_START)
        
        if result:
            print("Start failed.")
            return result
        
        return result
    
    def doStop(self):
        
        result = self.edrelib.EDRE_DAControl(self.analog0,0,2)
        
        if result:
            print("Stop failed.")
            st = (ctypes.c_char*256)()
            self.edrelib.EDRE_StrError(result,ctypes.byref(st))
            print(st.value)

    def makeSineWave(self,resolution,amplitude,offset):
        4
        inc = 2*np.pi/resolution
        
        data = (ctypes.c_double*resolution)()
        data_p = ctypes.cast(data,ctypes.POINTER(ctypes.c_double))
        
        for ii in range(resolution):
            data_p[ii] = ctypes.c_double(np.sin(inc*ii)*amplitude+offset)
        
        return resolution,data

    def makeWaveform(self,resolution,amplitude):
        
        chan = 1
        cont = 1
        offset = 0
        
        samples,buffer = self.makeSineWave(resolution,amplitude,offset)
        buffer_p = ctypes.cast(buffer,ctypes.POINTER(ctypes.c_double))
        
        data = (ctypes.c_long*(resolution+1)*4)()
        data_p = ctypes.cast(data,ctypes.POINTER(ctypes.c_long))
        
        for ii in range(resolution):
            for jj in range(4):
                data_p[ii*4+jj] = ctypes.c_long(round(buffer_p[ii]*1000000.0))
                
        for jj in range(4): 
            # /*add dummy for FIFO pointer loop mode bug*/
            data_p[resolution*4+jj] = 0
  
        return resolution,data_p
    
    def run(self):
        
        amplitude = 5
        
        samples, data_p = self.makeWaveform(1000,amplitude)
            
        self.doStart(samples,data_p)
        
        
if __name__ == "__main__":
    test = FIFO()
    test.doStop()
    test.query(202,0)
    test.query(201,0)
    test.write(0,500000)
    test.query(202,0)
    test.doStop()
    test.run()

        
        