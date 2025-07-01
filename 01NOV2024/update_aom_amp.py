from artiq.experiment import *
class Update_AOM_Freq(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
    @kernel
    def run(self):
        self.core.reset()
        self.urukul0_cpld.init()
        self.core.break_realtime()
        f = round(self.urukul0_ch0.get_frequency())
        delay(20*us)
        self.urukul0_ch0.set(frequency = f*Hz, amplitude = 1.0)
        self.core.wait_until_mu(now_mu())
