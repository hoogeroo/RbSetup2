from artiq.experiment import *
import time

class LiveUpdateAOM(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")  # Adjust channel ID as needed

    @rpc
    def get_frequency(self):
        """Fetch frequency from the host (replace with your live input method)."""
        
        return self.host_frequency_input

    def prepare(self):
        self.host_frequency_input = 80.0  # Initial frequency in MHz

    @kernel
    def set_frequency(self, freq_mhz):
        """Update AOM frequency."""
        self.core.break_realtime()
        self.urukul0_ch0.set(freq_mhz * MHz)  # Set frequency
        self.urukul0_ch0.sw.on()  # Ensure output is on
        self.core.break_realtime()

    def run(self):
        print("Live update AOM frequency experiment running...")
        while True:
            # Simulate a live update loop
            new_freq = self.get_frequency()
            self.set_frequency(new_freq)
            print(f"Frequency updated to: {new_freq} MHz")
            time.sleep(0.1)  # Prevent spamming, adjust as needed