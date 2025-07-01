#import artiq
from artiq.coredevice import ad9910
from artiq.experiment import *
from artiq.language.environment import EnvExperiment
from artiq.frontend import artiq_run
from artiq.language.core import (delay, kernel, )


class Fastino_Single_Output(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("fastino0")

    @kernel
    def run(self): 
        self.core.reset()
        self.core.break_realtime()
        self.fastino0.init()
        delay(200e-6)  
        while (1):
            self.fastino0.set_daq(1,1.0)
            delay(1.0)
            self.fastino0.set_dac(1,0.0)
            delay(1.0)
        


if __name__ == "__main__":
    artiq_run.run()
    pass
