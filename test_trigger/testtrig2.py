#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 15:54:25 2025

@author: rabi
"""

from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut, TTLIn

class LineTrigger(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl2")
        self.setattr_device("ttl4")
        
        
        
    @kernel
    def run(self):
        self.core.reset()
        while True:
            self.ttl2.wait_for_rising_edge()
            print("Signal Detected")
            self.ttl4.pulse(10*us)
            delay(17*us)
            
            