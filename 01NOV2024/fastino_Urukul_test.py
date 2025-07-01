from artiq.experiment import *
import numpy as np
import json
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch1')
    @kernel
    def init_dds(self, dds):
        self.core.break_realtime()
        self.urukul0_ch1.init()
        self.urukul0_ch1.set_att(0.*dB)
        self.urukul0_ch1.sw.on()
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.urukul0_cpld.init()
        self.init_dds(self.urukul0_ch1)
        #self.configure_ram_mode(self.urukul0_ch1)
        delay(10*ms)
        self.urukul0_ch1.set_cfr1(ram_enable=0)
        self.urukul0_ch1.sw.off()