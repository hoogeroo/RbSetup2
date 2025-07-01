from artiq.experiment import *
class Update_AOM_Freq(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
        self.setattr_device('urukul0_ch1')
        self.setattr_device('urukul0_ch2')
        self.setattr_device('urukul0_ch3')
    @kernel
    def run(self):
        self.core.reset()
        self.urukul0_ch1.cfg_sw(True)
        #self.urukul0_ch0.cfg_sw(True)
        self.urukul0_ch1.set(frequency = 86.0*MHz)
        delay(1e-3)
