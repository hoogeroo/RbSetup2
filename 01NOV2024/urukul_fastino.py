from artiq.experiment import *
import numpy as np
import json
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
    def prepare(self):
        self.voltage_arrays = [1.0,5.0,3.0,0.0,0.5,5,0.5,0.0]
    @kernel
    def record(self):
        with self.core_dma.record("test"):
            voltage_arrays = [1.0,5.0,3.0,0.0,0.5,5.0,0.0]
            frequency_arrays = [75,85,35,65,60,65,60]
            for i in range(len(voltage_arrays)):
                with parallel:
                  self.fastino0.set_dac(0, voltage_arrays[i])
                  self.urukul0_ch0.set(frequency_arrays[i]*MHz)
                delay(200 * ms)
    @kernel
    def run(self):
        self.core.reset()
        self.record()
        test = self.core_dma.get_handle("test")
        self.core.break_realtime()
        self.core_dma.playback_handle(test)
        