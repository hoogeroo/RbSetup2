#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 15:54:25 2025

@author: rabi
"""

from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut, TTLInOut

class LineTrigger(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl2")
        self.setattr_device("ttl4")
        
        
        
    @kernel
    def run(self):
        self.core.reset()
        self.ttl2.input()
        self.ttl4.output()
        while True:
            delay(17*ms)
            if self.ttl2.gate_rising(200*ms):
                self.ttl4.pulse(2*us)
 #               print("Detected!")
            else:
                print("TimeOut")