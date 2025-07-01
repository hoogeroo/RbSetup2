#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 12:54:35 2025

@author: rabi
"""
from artiq.experiment import *
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
        self.setattr_device('urukul0_ch1')
        self.setattr_device('urukul0_ch2')
        self.setattr_device('urukul0_ch3')
        self.setattr_device('ttl4')
    def prepare(self):
        self.a=32*[1]
        self.b=32*[2]
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.ttl4.on()
        delay(1*us)
        self.fastino0.set_group(0,self.a)
        delay(10*us)
        self.fastino0.set_group(0,self.b)
        delay(10*us)

        self.ttl4.off()