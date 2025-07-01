from artiq.experiment import *

class RealTimeUpdateExample(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")

    def prepare(self):
        self.dds_values = self.get_dataset("dds_values")
    @kernel
    def run(self):
        print(self.dds_values)
        
        