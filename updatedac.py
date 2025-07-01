from artiq.experiment import *
class ChangeDAC(EnvExperiment):
   def build(self):
      self.setattr_device('core')
      self.setattr_device('fastino0')
   @kernel
   def run(self):
      self.core.reset()
      self.fastino0.init()
      delay(1e-3)
      self.fastino0.set_dac(0,0.0)
      delay(1e-3)
