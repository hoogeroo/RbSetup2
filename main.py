from artiq.experiment import *

import numpy as np
import scipy as sp

from gui import *

class Device(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_ch0')

        self.stages = 5
        self.variables = [
            VariableTypeBool("Digital"),
            VariableTypeFloat("Analog"),
            VariableTypeFloat("Rf Magnitude"),
            VariableTypeFloat("Rf Freq (MHz)", 1.0, 100.0, 1.0)
        ]

        self.dc = np.zeros(len(self.variables))
        self.experiment = np.zeros((self.stages, len(self.variables) + 1))

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

        self.update_dc()

    @kernel
    def update_dc(self):
        self.core.break_realtime()

        # the indicies here need to match the order of the variables defined in `build()`
        digital = bool(self.dc[0])
        analog = float(self.dc[1])
        rf_magnitude = float(self.dc[2])
        rf_freq = float(self.dc[3])

        # update digital output
        if digital:
            self.ttl5.on()
        else:
            self.ttl5.off()

        # update analog output
        self.fastino0.set_dac(0, analog)

        # update rf output
        self.urukul0_ch0.set(rf_freq * MHz, amplitude=rf_magnitude)

    @kernel
    def run_experiment(self):
        self.core.break_realtime()

        # iterate through the stages and get their values
        for i in range(self.stages):
            digital = bool(self.experiment[i, 0])
            analog = float(self.experiment[i, 1])
            rf_magnitude = float(self.experiment[i, 2])
            rf_freq = float(self.experiment[i, 3])

            # update digital output
            if digital:
                self.ttl5.on()
            else:
                self.ttl5.off()

            # update analog output
            self.fastino0.set_dac(0, analog)

            # update rf output
            self.urukul0_ch0.set(rf_freq * MHz, amplitude=rf_magnitude)

            # wait for a short time to simulate the experiment duration
            delay(100 * us)
        
        # reset the device to the dc values
        self.update_dc()
