from artiq.experiment import *
class Update_AOM_Freq(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
        self.setattr_device('fastino0')
    @kernel
    def run(self):
        self.core.reset()
        self.fastino0.init()
        self.urukul0_cpld.init()
        self.urukul0_ch0.init()
        self.core.break_realtime()
        self.urukul0_ch0.sw.on()
        data = [5.0, 0.2586001822965218, 0.1, 5.0, 5.0, 5.0, 0.01, 0.5263157894736843] + (24*[0.0])
        with parallel:
          self.fastino0.set_group(0, data)
          self.urukul0_ch0.set(frequency = 90*MHz, amplitude = 1.0)
        