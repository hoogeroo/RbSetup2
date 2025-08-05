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
        self.setattr_device('fastino0')
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
        self.urukul0_ch0.cpld.init()
        self.urukul0_ch0.init()
        self.urukul0_ch0.cfg_sw(True)
        self.urukul0_ch0.set_att(6.0 * dB)

    # for some reason the `Dc` class type hint doesn't work but at runtime it works
    @kernel
    def update_dc(self, dc):
        self.core.break_realtime()

        # update digital output
        if dc.digital.constant_value():
            self.ttl5.on()
        else:
            self.ttl5.off()

        # update analog output
        self.fastino0.set_dac(0, dc.analog.constant_value())

        # update rf output
        self.urukul0_ch0.set(
            dc.rf_freq.constant_value() * MHz,
            amplitude=dc.rf_magnitude.constant_value()
        )

    @kernel
    def run_experiment(self, stages):
        # reset the cores timer for the new experiment
        self.core.break_realtime()

        # iterate through the stages and get their values
        for stage in stages:
            if not stage.enabled:
                continue

            # update digital output
            if stage.digital.is_constant():
                if stage.digital.constant_value():
                    self.ttl5.on()
                else:
                    self.ttl5.off()

            # update analog output
            if stage.analog.is_constant():
                self.fastino0.set_dac(0, stage.analog.constant_value())

            # update rf output
            if stage.rf_freq.is_constant() and stage.rf_magnitude.is_constant():
                self.urukul0_ch0.set(stage.rf_freq.constant_value() * MHz, amplitude=stage.rf_magnitude.constant_value())

            # wait for a short time to simulate the experiment duration
            delay(stage.time.constant_value() * ms)
