from artiq.experiment import *

import numpy as np
import scipy as sp

from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi

class Gui(QDialog):
    @host_only
    def __init__(self, device):
        super(Gui, self).__init__()
        self.device = device
        
        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        self.gui_variables = ["digital", "analog", "rf_magnitude", "rf_freq"]
        for var in self.gui_variables:
            getattr(self, var).setValue(getattr(self.device, var))
            getattr(self, var).valueChanged.connect(self.update_dc)

    def update_dc(self):
        for var in self.gui_variables:
            setattr(self.device, var, getattr(self, var).value())

        self.device.update_dc()


class Device(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_ch0')

        self.digital = 0
        self.analog = 0.0
        self.rf_magnitude = 1.0
        self.rf_freq = 10.0  # in MHz

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

        # update digital output
        if self.digital:
            self.ttl5.on()
        else:
            self.ttl5.off()

        # update analog output
        self.fastino0.set_dac(0, self.analog)

        # update rf output
        self.urukul0_ch0.set(self.rf_freq * MHz, amplitude=self.rf_magnitude)
