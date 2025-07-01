from artiq.experiment import *
import numpy as np
import json
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
    def prepare(self):
        with open("stages.json", "r") as f:
            stages = json.load(f)
        self.voltage_arrays = [np.array(stage[0], dtype=float) for stage in stages]
        self.timesteps = [stage[1] for stage in stages]
    @kernel
    def record(self):
        with self.core_dma.record("test"):
            for i in range(len(self.voltage_arrays)):
                voltages = self.voltage_arrays[i]
                timestep = self.timesteps[i]
                with parallel:
                  for channel in range(len(voltages)):
                      self.fastino0.set_dac(channel, voltages[channel])
                      #delay(0.05 * ms)
                  delay(timestep * ms)
    @kernel
    def run(self):
        self.core.reset()
        self.record()
        test = self.core_dma.get_handle("test")
        self.core.break_realtime()
        self.core_dma.playback_handle(test)
