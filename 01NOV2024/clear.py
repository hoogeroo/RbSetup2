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
    def run(self):
        self.core.reset()
        self.urukul0_cpld.init()
        self.core.break_realtime()
        
        self.urukul0_ch0.set(freq=0,amplitude =0)
        delay(20*ms)
        self.urukul0_ch1.set(freq=0,amplitude =0)
        delay(20*ms)

        self.urukul0_ch2.set(freq=0,amplitude =0)
        delay(20*ms)

        self.urukul0_ch3.set(freq=0,amplitude =0)
        
        # Add channels as needed