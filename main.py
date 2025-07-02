from artiq.experiment import *


class LED(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")

    @kernel
    def run(self):
        self.core.reset()
        self.ttl5.output()
        while True:
          delay(2*ms)
          self.ttl5.pulse(2*ms)
