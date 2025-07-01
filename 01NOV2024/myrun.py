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
        self.setattr_device('urukul0_ch2')
        self.setattr_device('urukul0_ch3')
        self.setattr_device('urukul1_cpld')
        self.setattr_device('urukul1_ch0')
        self.setattr_device('urukul1_ch1')
        self.setattr_device('urukul1_ch2')
        self.setattr_device('urukul1_ch3')
        self.setattr_device('ttl4')
    def prepare(self):
        with open("stages.json", "r") as f:
            stages = json.load(f)
        self.voltage_arrays = [np.array(stage[0], dtype=float) for stage in stages]
        self.AOM_arrays = [np.array(stage[1], dtype=float) for stage in stages]
    @kernel
    def run(self):
        self.core.reset()
        self.urukul1_cpld.init()
        self.urukul0_cpld.init()
        self.core.break_realtime()
        channels = [self.urukul0_ch0, self.urukul0_ch1, self.urukul0_ch2, self.urukul0_ch3,
                    self.urukul1_ch0, self.urukul1_ch1, self.urukul1_ch2, self.urukul1_ch3]
        self.urukul0_cpld.cfg_switches(15)
        self.urukul1_cpld.cfg_switches(15)
        for i in range(len(self.voltage_arrays)):
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

