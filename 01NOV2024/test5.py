from artiq.experiment import *

class PersistentAOMController(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")  # Modify as needed
        self.setattr_argument("initial_frequency", NumberValue(100.0, unit="MHz"), "Parameters")

    @kernel
    def run(self):
        self.core.reset()
        self.urukul0_cpld.init()
        self.urukul0_ch0.init()
        self.urukul0_ch0.cfg_sw(True)
        self.urukul0_ch0.set(self.initial_frequency * MHz)

        while True:
            # Wait for frequency update command (from host)
            freq = self.get_frequency_update()
            self.urukul0_ch0.set(freq * MHz)
            delay(1e-3)

    @rpc
    def get_frequency_update(self) -> float:
        """
        Dummy function to simulate RPC. Replace this with real communication logic.
        """
        return 100.0  # Default value, replace with actual communication mechanism
