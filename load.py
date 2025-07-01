from artiq.experiment import *
from artiq.language import *
import numpy as np
import json
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
        self.setattr_device('urukul0_ch1')
    def prepare(self):
        with open("load.json", "r") as f:
            stages = json.load(f)

    @kernel
    def run(self):
        self.core.reset()
        #self.urukul1_cpld.init()
        self.urukul0_cpld.init()
        self.core.break_realtime()
        channels = [self.urukul0_ch0, self.urukul0_ch1]
        for channel in channels:
            channel.cfg_sw(True)
            channel.set(frequency=85*MHz, amplitude = 1.0)
            delay(50*ns)
            
            
"""        for i in range(len(self.voltage_arrays)):
            voltages = self.voltage_arrays[i]
            AOM_array = self.AOM_arrays[i]
            u_params = [(AOM_array[j][0], AOM_array[j][1]) for j in range(8)]
            self.ttl4.on()
            for v in voltages:
                self.fastino0.set_group(0, v)
                delay(5*ms)
            for j in range(8):
                channels[j].set(frequency=int(u_params[j][0]) * MHz, amplitude=u_params[j][1])
                delay(5000*ns)
"""
