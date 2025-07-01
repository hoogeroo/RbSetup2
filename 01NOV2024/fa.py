from artiq.experiment import *
class Update_AOM_Freq(EnvExperiment):
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
    @kernel
    def run(self):
        self.core.reset()
        #self.urukul1_cpld.init()
        self.core.break_realtime()
        self.urukul1_cpld.init()
        #self.urukul1_ch0.init()


        #self.fastino0.set_group(0,32*[1])
        #self.urukul0_ch0.set(frequency = 70*MHz, amplitude = 1.0)
