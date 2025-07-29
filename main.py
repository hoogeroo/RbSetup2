'''
main.py: connects to the artiq device and starts the gui
'''

from artiq.experiment import *

import numpy as np
import scipy as sp

from gui import *
from value_types import *

class Device(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_ch0')

        self.variables = [
            VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0, 'ms'),
            VariableTypeBool("Digital", "digital"),
            VariableTypeFloat("Analog", "analog"),
            VariableTypeFloat("Rf Magnitude", "rf_magnitude"),
            VariableTypeFloat("Rf Freq (MHz)", "rf_freq", 1.0, 100.0, 1.0, 'MHz')
        ]

    @host_only
    def run(self):
        self.init_device()

        app = QApplication([])
        gui = Gui(self)
        gui.show()
        app.exec()

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
