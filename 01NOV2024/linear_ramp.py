
from artiq.experiment import *
import numpy as np
import json

class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
    def prepare(self):


        # Parameters
        start = 5  # Peak value
        end = 1    # Asymptotic value
        t0 = 0      # Peak position (center of Lorentzian)
        gamma = 5   # Width parameter

        # Compute parameters
        C = end
        A = start - end

        # Lorentzian decay function
        def lorentzian_decay(t, A, gamma, t0, C):
            return A * gamma**2 / ((t - t0)**2 + gamma**2) + C

        # Generate time points, focusing only on the decay region
        time = np.linspace(0, 20, 3000)  # Only after the peak

        # Generate Lorentzian decay curve
        self.voltage_ramp = lorentzian_decay(time, A, gamma, t0, C)
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.fastino0.set_dac(0,5.0)
        delay(50*ms)
        voltages = self.voltage_ramp
        for i in range(len(voltages)):

            self.fastino0.set_dac(0,voltages[i])
            delay(0.05*ms)
            #print(voltages[i])
            #delay(0.05 * ms)
"""        self.core.reset()
        self.record()
        test = self.core_dma.get_handle("test")
        self.core.break_realtime()
        self.core_dma.playback_handle(test)"""
        #delay(0.5*ms)
        #self.fastino0.set_dac(0,0.0)
