from artiq.experiment import *
from artiq.language import *
#import numpy as np
#import json
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul1_cpld')
    @kernel
    def run(self):
        self.core.reset()
        self.urukul0_cpld.init()
        self.urukul1_cpld.init()