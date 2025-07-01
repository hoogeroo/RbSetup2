from artiq.experiment import *
class ChangeDAC(EnvExperiment):
   def build(self):
      self.setattr_device('core')
      self.setattr_device('fastino0')
   @kernel
   def run(self):
      self.core.reset()
      delay(1e-3)
      self.fastino0.set_dac(7,2.5)
      delay(1e-3)
