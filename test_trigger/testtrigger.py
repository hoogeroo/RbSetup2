#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 13:55:39 2025

@author: rabi
"""

from artiq.experiment import *


class LineTrigger(EnvExperiment):

    def build(self):
        self.setattr_argument("use_line_trigger", BooleanValue(default=True))
        self.setattr_device("core")
        self.setattr_device("ttl2")
        self.setattr_device("ttl4")

    @kernel
    def wait_for_line1(self, trig_delay):
        """Wait for line trigger with configurable delay

        :trig_delay: delay after line trigger in s
        """
        t_gate = self.ttl2.gate_rising(20*ms)
        t_trig = self.ttl2.timestamp_mu(t_gate)
        at_mu(t_trig)
        delay(trig_delay)

    @kernel
    def wait_for_line2(self, trig_delay):
        """Wait for line trigger with configurable delay

        :trig_delay: delay after line trigger in s
        """
        while True:
            t_gate = self.ttl2.gate_rising(10*ms)
            t_trig = self.ttl2.timestamp_mu(t_gate)
            if t_trig > 0:
                at_mu(t_trig)
                delay(trig_delay)
                break
            delay(10*us) # No trigger, try again

    @kernel
    def run(self):
        self.core.reset()
        while True:
            if (self.use_line_trigger):
                self.wait_for_line1(100*us)
                #self.wait_for_line2(100*us)
            self.ttl4.pulse(10*us)
            delay(50*ms)
            