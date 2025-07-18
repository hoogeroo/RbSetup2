from artiq.experiment import *

import numpy as np
import scipy as sp

from gui import *

# dummy class used to represent the device's digital and analog outputs
# this class will be fill with ids set in the variables array then 
# sent to the device
class Dc:
    def __init__(self):
        pass

# same as above but for an experiment stage
class Stage:
    def __init__(self):
        pass

class Device(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_ch0')

        self.stages = 5
        self.variables = [
            VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0),
            VariableTypeBool("Digital", "digital"),
            VariableTypeFloat("Analog", "analog"),
            VariableTypeFloat("Rf Magnitude", "rf_magnitude"),
            VariableTypeFloat("Rf Freq (MHz)", "rf_freq", 1.0, 100.0, 1.0)
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
    def run_experiment(self, stages):
        self.core.break_realtime()

        # iterate through the stages and get their values
        for stage in stages:
            # update digital output
            if stage.digital:
                self.ttl5.on()
            else:
                self.ttl5.off()

            # update analog output
            self.fastino0.set_dac(0, stage.analog)

            # update rf output
            self.urukul0_ch0.set(stage.rf_freq * MHz, amplitude=stage.rf_magnitude)

            # wait for a short time to simulate the experiment duration
            delay(stage.time * ms)
