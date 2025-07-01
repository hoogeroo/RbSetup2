#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 08:43:36 2019

@author: lab
"""

import ctypes

samples = 100

data = (ctypes.c_int16*samples*24)()
data_p = ctypes.cast(data,ctypes.POINTER(ctypes.c_int16))
        
#for ii in range(24):
#    for jj in range(samples):
#        data_p[ii*samples+jj] = ctypes.c_int16(self.floatToInt16(values[ii][jj]))