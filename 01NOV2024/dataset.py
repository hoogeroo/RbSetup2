from artiq.experiment import *
import numpy as np
import time
import json
class Datasets(EnvExperiment):
    """Dataset tutorial"""
    def build(self):
        self.setattr_device("core") # no devices used
    def prepare(self):
        with open("amp_frequencies.json", "r") as f:
            self.dds_values = json.load(f)
    @kernel
    def run(self):
        self.set_dataset("dds_values", self.dds_values, broadcast=True,persist=True)
        