from artiq.experiment import *
class Update_AOM_Freq(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        stored_amp=self.urukul0_ch0.asf_to_amplitude(self.urukul0_ch0.get_mu()[2])
        delay(20*us)
        self.urukul0_ch0.set(94.0*MHz, amplitude = stored_amp)
