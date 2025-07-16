from artiq.experiment import *

import numpy as np
import scipy as sp

from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi

class Gui(QDialog):
    def __init__(self, device):
        super(Gui, self).__init__()
        self.device = device
        
        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        self.submit.clicked.connect(self.submit_function)

    def submit_function(self):
        self.textdisplay.setText(f"Input 1: {self.input1.text()}\nInput 2: {self.input2.text()}")
        self.device.pulse()

    def pulse(self):
        self.device.pulse()

class Device(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_ch0')

    def run(self):
        app = QApplication([])
        gui = Gui(self)
        gui.show()
        app.exec()

        self.pulse()
        

    @kernel
    def pulse(self):
        print("Switched context")

        self.core.reset()
        self.fastino0.init()
        self.urukul0_ch0.cpld.init()
        self.urukul0_ch0.init()

        # pulse ttl (digital)
        self.ttl5.on()

        # signal on urukul dds (rf)
        self.urukul0_ch0.cfg_sw(True)
        self.urukul0_ch0.set(np.pi * MHz)
        self.urukul0_ch0.set_att(6.0*dB)

        # ramp on fastino (analog)
        samples = 256
        duration = 100 * ms
        for i in range(samples):
            self.fastino0.set_dac(0, i / samples)

            delay(duration / samples)

        self.ttl5.off()
        self.urukul0_ch0.cfg_sw(False)

        # self.core.wait_until_mu(now_mu())
        print("Queued pulse!")

    # def prepare(self):
    #     self.period = 0.1 * s
    #     self.sample = 128
    #     t = np.linspace(0, 1, self.sample)
    #     self.voltages = 4 * sp.signal.sawtooth(2 * np.pi * t, 0.5)
    #     self.interval = self.period/self.sample
    
    # @kernel
    # def run(self):
    #     self.core.reset()
    #     self.core.break_realtime()
    #     self.fastino0.init()

    #     delay(1*ms)

    #     counter = 0
    #     while True:
    #         self.fastino0.set_dac(0, self.voltages[counter])
    #         self.ttl5.pulse(self.interval / 2)
    #         counter = (counter + 1) % self.sample
    #         delay(self.interval)
