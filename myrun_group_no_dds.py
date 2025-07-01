from artiq.experiment import *
import numpy as np
import json
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
    def prepare(self):
        with open("stages.json", "r") as f:
            stages = json.load(f)
        self.voltage_arrays = [np.array(stage[0], dtype=float) for stage in stages]
        self.timesteps = [stage[1] for stage in stages]
    @kernel
    #def record(self):
    def record(self):
        with self.core_dma.record("test"):
            for i in range(len(self.voltage_arrays)):
                voltages = self.voltage_arrays[i]
                timestep = self.timesteps[i]
                array = [0.0] * 32  # Use a regular list
                for j in range(8):  # Copy first 8 values
                    array[j] = voltages[j]
                with parallel:
                    self.fastino0.set_group(0, array)
                delay(timestep * ms)
                """with self.core_dma.record("test"):
            for i in range(len(self.voltage_arrays)):
                voltages = self.voltage_arrays[i]
                timestep = self.timesteps[i]
                array = np.zeros(32, dtype=float)
                array[:8] = voltages
                with parallel:
                  self.fastino0.set_group(0, array)
                delay(timestep * ms)"""
    @kernel
    def run(self):
        self.core.reset()
        self.record()
        test = self.core_dma.get_handle("test")
        self.core.break_realtime()
        self.core_dma.playback_handle(test)
