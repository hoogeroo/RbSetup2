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

        dc = np.zeros(len(self.variables), dtype=np.float32)
        experiment = np.zeros((self.stages, len(self.variables) + 1), dtype=np.float32)

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
        pass

        # self.core.break_realtime()

        # # update digital output
        # if self.digital:
        #     self.ttl5.on()
        # else:
        #     self.ttl5.off()

        # # update analog output
        # self.fastino0.set_dac(0, self.analog)

        # # update rf output
        # self.urukul0_ch0.set(self.rf_freq * MHz, amplitude=self.rf_magnitude)
