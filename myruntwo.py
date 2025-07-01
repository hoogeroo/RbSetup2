from artiq.experiment import *
#from artiq.language.environment import EnvExperiment
from artiq.frontend import artiq_run
#from artiq.language.core import (delay, kernel, )
#from artiq.language.units import ms

class Fastino_Test(EnvExperiment):
    def build(self):        
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("fastino0")
        
        self.data_1 = [2 for _ in range(0, 32)]
        self.data_2 = [0 for _ in range(0, 32)] 
        #self.data_0 = [0.0 for _ in range(0, 32)]
    @kernel
    def record(self):
       with self.core_dma.record("test_sequence"):
           self.fastino0.init()
           for _ in range(0, 100):
               self.fastino0.set_group(0, self.data_1)                  
               delay(10 * ms)
               self.fastino0.set_group(0, self.data_2)                  
               delay(10 * ms)
               self.fastino0.set_group(0, self.data_1)                  
               delay(10 * ms)
               self.fastino0.set_group(0, self.data_2)                  
               delay(10 * ms)
    @kernel
    def run(self):
        self.core.reset()

        delay(10*ms)
        self.record()
        test_sequence = self.core_dma.get_handle("test_sequence")
        self.core.break_realtime()
        self.core_dma.playback_handle(test_sequence)
        channel = self.fastino0.width
        print(channel)
        #print(self.fastino0.log2_width)
        #self.get_device_db()

        #print(self.data_1,self.data_2)

