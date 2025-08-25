'''
main.py: connects to the artiq device and starts the gui
'''

import numpy as np
import scipy as sp

from device import AbstractDevice
from gui import *
from value_types import *

from artiq.experiment import *

class Device(AbstractDevice, EnvExperiment):
    def build(self):
        # initializes the variables for the device and gui
        AbstractDevice.build(self)

        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device("ttl6")
        self.setattr_device('fastino0')
        self.setattr_device("sampler0")
        self.setattr_device('urukul0_ch0')

    @host_only
    def run(self):
        self.init_device()

        # runs the gui in a separate process
        AbstractDevice.run(self)

    @kernel
    def init_device(self):
        self.core.reset()
        self.fastino0.init()
        self.sampler0.init()
        self.sampler0.set_gain_mu(0, 0)
        self.urukul0_ch0.cpld.init()
        self.urukul0_ch0.init()
        self.urukul0_ch0.cfg_sw(True)
        self.urukul0_ch0.set_att(6.0 * dB)

    # for some reason the `Dc` class type hint doesn't work but at runtime it works
    @kernel
    def update_dc(self, dc):
        self.core.break_realtime()

        # update digital output
        if dc.digital:
            self.ttl5.on()
        else:
            self.ttl5.off()

        # update analog output
        self.fastino0.set_dac(0, dc.analog)

        # update rf output
        self.urukul0_ch0.set(
            dc.rf_freq * MHz,
            amplitude=dc.rf_magnitude
        )

    @kernel
    def run_experiment_device(self, stages):
        # reset the cores timer for the new experiment
        self.core.break_realtime()

        # iterate through the stages and get their values
        for i in range(len(stages.time)):
            # update digital output
            if stages.digital[i]:
                self.ttl5.on()
            else:
                self.ttl5.off()

            # update analog output
            self.fastino0.set_dac(0, stages.analog[i])

            # update rf output
            self.urukul0_ch0.set(stages.rf_freq[i] * MHz, amplitude=stages.rf_magnitude[i])

            # wait for a short time to simulate the experiment duration
            delay(stages.time[i] * ms)

    @kernel
    def pulse_push_laser(self):
        # push the laser for a short time
        self.core.break_realtime()
        self.ttl6.on()
        delay(10 * ms)
        self.ttl6.off()
    
    @kernel
    def read_fluorescence(self) -> float:
        # read the fluorescence signal
        self.core.break_realtime()
        sample = [0.0]*8
        self.sampler0.sample(sample)
        return sample[0]
