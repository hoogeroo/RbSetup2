from artiq.experiment import *

class RealTimeUpdateExample(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")

    def prepare(self):
        # Initialize or update the dataset
        self.set_dataset("frequency", 10e6, broadcast=True)

    @kernel
    def run(self):
        self.core.reset()
        self.urukul0_cpld.init()
        self.urukul0_ch0.init()

        # Retrieve the current frequency from the dataset
        freq = self.get_dataset("frequency")
        self.urukul0_ch0.set(freq)
        self.urukul0_ch0.sw.on()
