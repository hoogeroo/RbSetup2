from artiq.experiment import *
from artiq.coredevice.ad9910 import AD9910

class SetUrukulChannels(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        #self.setattr_device("urukul0")
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.setattr_device("urukul0_ch2")
        self.setattr_device("urukul0_ch3")

    def run(self):
        self.core.reset()
        self.urukul0_cpld.init()
        self.core.break_realtime()
        # Frequency in Hz and Amplitude in dB for each channel
        freqs = [100e6, 150e6, 200e6, 250e6]  # example frequencies for channels 1-4
        amps = [0.5, 0.7, 0.6, 0.8]  # example amplitudes (normalized)
        
        # Set the frequencies and amplitudes for all channels
        for ch, freq, amp in zip([self.urukul0_ch0, self.urukul0_ch1, self.urukul0_ch2, self.urukul0_ch3], freqs, amps):
            ch.set(frequency = freq*Hz,amplitude = amp)
            delay(50*us)
        # Enable the channels simultaneously
        #self.urukul0_ch0.enable()
       #self.urukul0_ch1.enable()
        #self.urukul0_ch2.enable()
        #self.urukul0_ch3.enable()
        
        # Optionally, add a delay or trigger a waveform to start output
        delay(1)  # Delay to allow the channels to stabilize
